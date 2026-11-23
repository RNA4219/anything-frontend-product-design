# Pre-scoring correction of the comparison tests

The original task and v1 suite remain unchanged under their original hashes.
No v1 or v2 suite had been executed against either generated arm when this
correction was made. The baseline builder had reported its own smoke checks;
those were not the campaign scoring results. The independent critic inspected
the task and suite without inspecting either generated implementation.

The task explicitly allows replay of an identical request ID and payload for
24 hours. V1 T03 required exactly one submission and several other trials
required canSubmit=false even in a state where safe replay is permitted.
Those assertions test one UI strategy rather than the contractual safety
property. They can reject a correct alternative. V1 is therefore retained as
an invalidated evaluation artifact, not used to calculate an effectiveness claim.

V2 preserves the same task, 12 scenario identities and expected business
outcomes. It removes blanket canSubmit=false assertions in T03/T05/T06/T10/T12
and checks that attempted recovery does not produce a different request/payload
or more than one effect in the lost-response fixture. T12 also checks this
property after a non-authoritative lookup miss. No generated arm is changed
in response to these tests. V2 is separately hashed before scored execution.

The critic also noted that T07's sequential observation does not test response
reordering. Additional concurrent-response regression trials will be reported
separately, with their provenance; they are not silently counted as the original
12 scenarios or as a statistical holdout.

## V3 correction before either arm was scored

Independent negative controls also passed v1 while sending the wrong booking or cancellation target, and while rendering contradictory outcome text. V3 enforces mutation/cancel target identity and adds T13/T14 for late cancellation acknowledgement/error after a verified success. Those two races are additional regression cases. Message truthfulness remains a separate implementation/DOM review requirement; it is not claimed to follow from automated controller scoring. V1 and V2 are both retained.

## v4：独立プローブによる残存条件の修正

v3でbaselineが14/14だったことは観測済み、candidateは未採点。Criticは両生成物を未閲覧。T04を照会前後の送信差分・同一意図・副作用数に修正し、安全な即時再送を許可した。T13/T14はcanCheckに応じて並行／直列の取消経路を検証し、契約にない並行操作の義務を除去した。v3と結果は保持。v4は両群に同条件で適用する。文言の真偽は別途DOMとコードを検査する。
