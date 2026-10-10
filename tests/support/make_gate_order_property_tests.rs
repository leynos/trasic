//! Generated semantic and malformed-frame contracts for the Make gate recorder.

use std::collections::BTreeMap;

use proptest::{collection::vec, option, prelude::*};

use super::{ENVIRONMENT_NAMES, EnvironmentValue, Invocation, SecretPresence, parse_invocations};
use crate::property_fields::{self, GeneratedEnvironment, RecordData};

/// Generated Make-specific semantics beyond the common invocation fields.
#[derive(Clone, Debug)]
struct GateData {
    /// Common environment and argument data, independent of the parser.
    record: RecordData,
    /// Semantic gate-stage field, preserving arbitrary Unicode.
    stage: String,
    /// Semantic private-cache observation, preserving arbitrary Unicode.
    cache_state: String,
    /// Optional query output, including a present but empty value.
    result: Option<String>,
    /// Independently generated redacted secret presence for each secret field.
    secrets: (bool, bool),
}

/// Generates a complete semantic Make observation without subprocess operations.
fn record() -> impl Strategy<Value = GateData> {
    (
        property_fields::record(23),
        property_fields::field(),
        property_fields::field(),
        option::of(property_fields::field()),
        (any::<bool>(), any::<bool>()),
    )
        .prop_map(|(record, stage, cache_state, result, secrets)| GateData {
            record,
            stage,
            cache_state,
            result,
            secrets,
        })
}

/// Encodes the gate-specific protocol tail, allowing deliberate count corruption.
fn fields(data: &GateData, count: usize) -> Vec<String> {
    let mut result = property_fields::header(&data.record, ENVIRONMENT_NAMES);
    for (name, is_present) in [
        ("CS_ACCESS_TOKEN", data.secrets.0),
        ("GITHUB_TOKEN", data.secrets.1),
    ] {
        result.extend(
            [
                "secret",
                name,
                if is_present { "present" } else { "absent" },
            ]
            .map(str::to_owned),
        );
    }
    result.extend(["stage", &data.stage, "cache-state", &data.cache_state].map(str::to_owned));
    property_fields::arguments(&mut result, &data.record.arguments, count);
    result.extend(
        [
            "result-state",
            if data.result.is_some() {
                "value"
            } else {
                "none"
            },
            "result",
            data.result.as_deref().unwrap_or(""),
            "end-invocation",
        ]
        .map(str::to_owned),
    );
    result
}

/// Computes expected semantic values independently of the parsing functions.
fn expected(data: &GateData) -> Invocation {
    let environment = ENVIRONMENT_NAMES
        .iter()
        .zip(&data.record.environment)
        .map(|(name, value)| {
            let state = match value {
                GeneratedEnvironment::Unset => EnvironmentValue::Unset,
                GeneratedEnvironment::Empty => EnvironmentValue::Empty,
                GeneratedEnvironment::Value(text) => EnvironmentValue::Value(text.clone()),
            };
            ((*name).to_owned(), state)
        })
        .collect::<BTreeMap<_, _>>();
    let secrets = [
        ("CS_ACCESS_TOKEN", data.secrets.0),
        ("GITHUB_TOKEN", data.secrets.1),
    ]
    .into_iter()
    .map(|(name, is_present)| {
        (
            name.to_owned(),
            if is_present {
                SecretPresence::Present
            } else {
                SecretPresence::Absent
            },
        )
    })
    .collect();
    Invocation {
        executable: data.record.executable.clone(),
        working_directory: data.record.working_directory.clone(),
        arguments: data.record.arguments.clone(),
        environment,
        secrets,
        stage: data.stage.clone(),
        cache_state: data.cache_state.clone(),
        result: data.result.clone(),
    }
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(64))]

    /// Generated streams preserve Unicode, states, argv, query output, and order.
    #[test]
    fn generated_streams_round_trip_semantically(records in vec(record(), 0..5)) {
        let log = records.iter().map(|data| {
            property_fields::frame(&fields(data, data.record.arguments.len()))
        }).collect::<String>();
        let wanted = records.iter().map(expected).collect::<Vec<_>>();
        let actual = parse_invocations(log.as_bytes()).map_err(|error| TestCaseError::fail(error.to_string()))?;
        prop_assert_eq!(actual, wanted, "generated Make records must preserve every semantic field");
    }

    /// Unlike Act, Make gate logs require their final NUL and closing marker.
    #[test]
    fn malformed_framing_and_counts_are_rejected(data in record()) {
        let valid_fields = fields(&data, data.record.arguments.len());
        let unterminated = valid_fields.join("\0");
        prop_assert!(parse_invocations(unterminated.as_bytes()).is_err(), "Make must reject a missing terminal NUL");
        let log = property_fields::frame(&valid_fields);
        prop_assert!(parse_invocations(format!("{log}\0").as_bytes()).is_err(), "an extra NUL field cannot form a record");
        let mut incomplete = valid_fields;
        drop(incomplete.pop());
        prop_assert!(parse_invocations(property_fields::frame(&incomplete).as_bytes()).is_err(), "a missing closing marker must fail");
        let wrong_count = property_fields::frame(&fields(&data, data.record.arguments.len() + 200));
        prop_assert!(parse_invocations(wrong_count.as_bytes()).is_err(), "declared counts exceeding available fields must fail");
        let mut undercounted = data;
        undercounted.record.arguments.insert(0, "not-a-protocol-marker".to_owned());
        let short_count = property_fields::frame(&fields(&undercounted, 0));
        prop_assert!(parse_invocations(short_count.as_bytes()).is_err(), "underdeclared arguments must not hide a non-marker field");
        let mut invalid_utf8 = vec![0xff];
        invalid_utf8.extend_from_slice(log.as_bytes());
        prop_assert!(parse_invocations(&invalid_utf8).is_err(), "non-UTF-8 executor fields must fail");
    }
}
