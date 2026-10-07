//! Generated semantic and malformed-record contracts for the Act Make recorder.

use std::collections::BTreeMap;

use proptest::{collection::vec, prelude::*};

use super::{EnvironmentValue, GitHubToken, Invocation, parse_invocations};
use crate::property_fields::{self, GeneratedEnvironment, RecordData};

/// Independent expected schema, including Act's additional environment selection.
const ENVIRONMENT_NAMES: &[&str] = &[
    "WITH_ACT",
    "ACT",
    "RUSTFLAGS",
    "CARGO_ENCODED_RUSTFLAGS",
    "CARGO_PROFILE_DEV_CODEGEN_BACKEND",
    "CARGO_BUILD_TARGET",
    "CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER",
];

/// Generates each redacted token-presence state independently from environment.
fn token() -> impl Strategy<Value = &'static str> {
    prop_oneof![Just("unset"), Just("empty"), Just("present")]
}

/// Encodes the Act-specific tail; counts can deliberately disagree with arguments.
fn fields(data: &RecordData, token_state: &str, count: usize) -> Vec<String> {
    let mut result = property_fields::header(data, ENVIRONMENT_NAMES);
    result.extend(["secret", "GITHUB_TOKEN", token_state].map(str::to_owned));
    property_fields::arguments(&mut result, &data.arguments, count);
    result.push("end-invocation".to_owned());
    result
}

/// Converts independent generated data into the semantic result Act must return.
fn expected(data: &RecordData, token_state: &str) -> Invocation {
    let environment = ENVIRONMENT_NAMES
        .iter()
        .zip(&data.environment)
        .map(|(name, value)| {
            let state = match value {
                GeneratedEnvironment::Unset => EnvironmentValue::Unset,
                GeneratedEnvironment::Empty => EnvironmentValue::Empty,
                GeneratedEnvironment::Value(text) => EnvironmentValue::Value(text.clone()),
            };
            ((*name).to_owned(), state)
        })
        .collect::<BTreeMap<_, _>>();
    let github_token = match token_state {
        "unset" => GitHubToken::Unset,
        "empty" => GitHubToken::Empty,
        _ => GitHubToken::Present,
    };
    Invocation {
        executable: data.executable.clone(),
        working_directory: data.working_directory.clone(),
        arguments: data.arguments.clone(),
        environment,
        github_token,
    }
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(64))]

    /// Generated records preserve Unicode, empty fields, states, argv, and order.
    #[test]
    fn generated_streams_round_trip_semantically(
        records in vec((property_fields::record(7), token()), 0..5),
    ) {
        let log = records.iter().map(|(data, state)| {
            property_fields::frame(&fields(data, state, data.arguments.len()))
        }).collect::<String>();
        let wanted = records.iter().map(|(data, state)| expected(data, state)).collect::<Vec<_>>();
        let actual = parse_invocations(&log).map_err(|error| TestCaseError::fail(error.to_string()))?;
        prop_assert_eq!(actual, wanted, "generated Act records must preserve every semantic field");
    }

    /// Act intentionally accepts a complete record without its optional final NUL.
    #[test]
    fn complete_unterminated_records_keep_historical_acceptance(
        data in property_fields::record(7), state in token(),
    ) {
        let log = fields(&data, state, data.arguments.len()).join("\0");
        let actual = parse_invocations(&log).map_err(|error| TestCaseError::fail(error.to_string()))?;
        prop_assert_eq!(actual, vec![expected(&data, state)], "Act's optional terminal NUL must retain its contract");
    }

    /// Appended empty fields, incomplete closing frames, and excess counts fail.
    #[test]
    fn malformed_streams_and_counts_are_rejected(
        data in property_fields::record(7), state in token(),
    ) {
        let valid_fields = fields(&data, state, data.arguments.len());
        let log = property_fields::frame(&valid_fields);
        prop_assert!(parse_invocations(&format!("{log}\0")).is_err(), "extra NUL fields cannot form an invocation");
        let mut incomplete = valid_fields;
        drop(incomplete.pop());
        prop_assert!(parse_invocations(&property_fields::frame(&incomplete)).is_err(), "a missing closing marker must fail");
        let wrong_count = property_fields::frame(&fields(&data, state, data.arguments.len() + 200));
        prop_assert!(parse_invocations(&wrong_count).is_err(), "declared counts exceeding available fields must fail");
        let mut undercounted = data;
        undercounted.arguments.insert(0, "not-a-protocol-marker".to_owned());
        let short_count = property_fields::frame(&fields(&undercounted, state, 0));
        prop_assert!(parse_invocations(&short_count).is_err(), "underdeclared arguments must not hide a non-marker field");
    }
}
