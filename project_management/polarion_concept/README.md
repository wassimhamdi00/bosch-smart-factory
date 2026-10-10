# Polarion ALM — conceptual data model

The six diagrams in this directory illustrate how project requirements, planned work, test cases, test runs, defects and change requests could be linked in an ALM system. **They are original concept diagrams, not Polarion screenshots, exports or evidence of configured work items.** Field sets and workflow states would need confirmation in a real deployment.

## Work-item mapping

| Project record | Proposed ALM type |
| --- | --- |
| REQ-001 to REQ-015 | Requirement |
| AP-01 to AP-10 | Task |
| TEST-001 to TEST-013 | Test case |
| CR-001 | Change request |
| DEF-001 | Defect |

## Traceability scenario

CR-001 changes REQ-012 from 2.0 s in baseline B1 to 1.0 s in baseline B2. The change is mapped to AP-08/AP-09 and TEST-010. The corresponding [simulated result](../evidence/simulated_runs.csv) (RUN-004) fails at a hypothetical 1.4 s, generating a modeled defect, DEF-001.

All 15 requirements have planned test-case links. This is traceability coverage, **not test execution coverage**. Five simulated runs are recorded; they are distinct from the Python unit tests.

## Concept views

- Requirements grid and requirement details
- Planned test coverage
- Change-impact relationships
- Simulated test-run review
- Hypothetical defect record

Reference documentation: [Polarion QA](https://www.siemens.com/en-gb/products/polarion/qa/) and [Polarion Requirements](https://www.siemens.com/de-de/products/polarion/requirements/), accessed 2026-10-09.
