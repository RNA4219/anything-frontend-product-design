# Checked tool boundaries

Public tools pinned: imozuru `30c3b59a076ce228f05aa3036809297422f23dee`; sankai `0e2521453ad758cfb680110da0fdddc994d000be`. Their README, SKILL, scripts and actual CLI usage were read.

- imozuru: parent orchestrates two real independent research agents; agents explicitly perform fetch and citation following under the user contract. No nested agents. Direct fetch failures are recorded separately from Web-reader fallbacks. Only successful original text reads support claims.
- sankai: analyst executes the decomposition / understanding / dissolution instructions as a skill. It has no dedicated decomposition CLI, execution or registration capability. Parent owns synthesis and registration.
- GitHub CLI: no signed-in gh session; connected GitHub tools are available. Git read clone succeeded. Publication uses the existing connection if local push is unavailable.
- Subagents: formal collaboration.spawn_agent is present. Parent plus two researchers = three simultaneous agents. Fresh analysis and evaluation threads follow; no recursive spawning. Same-model review is not objective human evidence.
