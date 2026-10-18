# Test Plan

| ID | Scenario | Expected result |
|---|---|---|
| T01 | Valid course and ratings 1–5 | Submission saved |
| T02 | Missing course | Rejected with validation message |
| T03 | Rating 0 or 6 | Rejected |
| T04 | Non-integer rating/course | Rejected without server crash |
| T05 | Comment over 1,000 characters | Rejected |
| T06 | Unknown/inactive course | Rejected |
| T07 | Empty feedback database | Dashboard explains insufficient data |
| T08 | Group below minimum threshold | Group omitted from averages |
| T09 | MySQL unavailable | Health API returns 503 |
| T10 | Enough valid data | Summary and applicable charts generated |
| T11 | CSV export | Aggregates exported; comments excluded |
| T12 | Dashboard viewed | Comment text is never rendered |

Before submission, record actual manual test results on the demonstration machine. Test syntax, database failure, empty data, boundary ratings, and successful end-to-end submission.
