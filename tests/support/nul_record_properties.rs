//! Pure generated data and NUL framing for the two command-recorder protocols.

use proptest::{collection::vec, prelude::*};

/// A generated environment state independent of either parser's representation.
#[derive(Clone, Debug)]
pub(super) enum GeneratedEnvironment {
    /// No variable reached the child process.
    Unset,
    /// The child received a present, empty variable.
    Empty,
    /// The child received this non-empty Unicode value.
    Value(String),
}

impl GeneratedEnvironment {
    /// Returns the protocol state and raw field, e.g. an empty state's empty field.
    pub(super) fn fields(&self) -> (&str, &str) {
        match self {
            Self::Unset => ("unset", ""),
            Self::Empty => ("empty", ""),
            Self::Value(value) => ("value", value),
        }
    }
}

/// Semantic invocation data that each protocol must recover independently.
#[derive(Clone, Debug)]
pub(super) struct RecordData {
    /// Unicode executable identity, including possible whitespace or emptiness.
    pub(super) executable: String,
    /// Unicode working directory field; no filesystem operations occur.
    pub(super) working_directory: String,
    /// Exactly one generated state for each protocol environment field.
    pub(super) environment: Vec<GeneratedEnvironment>,
    /// Arguments include empty values and arbitrary NUL-free Unicode fields.
    pub(super) arguments: Vec<String>,
}

/// Generates any Unicode character except the framing delimiter.
fn field_character() -> impl Strategy<Value = char> {
    any::<char>().prop_filter("NUL separates protocol fields", |character| {
        *character != '\0'
    })
}

/// Generates bounded NUL-free Unicode fields, including empty and control values.
pub(super) fn field() -> BoxedStrategy<String> {
    prop_oneof![
        Just(String::new()),
        Just("tab\tline\n".to_owned()),
        vec(field_character(), 0..40).prop_map(|characters| characters.into_iter().collect()),
    ]
    .boxed()
}

/// Generates all environment states while keeping value fields non-empty.
fn environment() -> impl Strategy<Value = GeneratedEnvironment> {
    prop_oneof![
        Just(GeneratedEnvironment::Unset),
        Just(GeneratedEnvironment::Empty),
        vec(field_character(), 1..40)
            .prop_map(|characters| GeneratedEnvironment::Value(characters.into_iter().collect())),
    ]
}

/// Generates one record with a fixed schema size, e.g. seven Act environment fields.
pub(super) fn record(environment_count: usize) -> BoxedStrategy<RecordData> {
    (
        field(),
        field(),
        vec(environment(), environment_count),
        vec(field(), 0..8),
    )
        .prop_map(
            |(executable, working_directory, environment, arguments)| RecordData {
                executable,
                working_directory,
                environment,
                arguments,
            },
        )
        .boxed()
}

/// Serializes only the common header and environment portion of either protocol.
pub(super) fn header(record: &RecordData, names: &[&str]) -> Vec<String> {
    let mut fields = vec![
        "invocation-v1".to_owned(),
        record.executable.clone(),
        record.working_directory.clone(),
    ];
    for (name, environment) in names.iter().zip(&record.environment) {
        let (state, value) = environment.fields();
        fields.extend(["env", name, state, value].map(str::to_owned));
    }
    fields
}

/// Emits the counted argument portion, permitting deliberately invalid counts.
pub(super) fn arguments(fields: &mut Vec<String>, values: &[String], declared_count: usize) {
    fields.extend([
        "argc".to_owned(),
        declared_count.to_string(),
        "argv".to_owned(),
    ]);
    fields.extend(values.iter().cloned());
}

/// Joins complete fields with the recorder's terminal NUL delimiter.
pub(super) fn frame(fields: &[String]) -> String { format!("{}\0", fields.join("\0")) }
