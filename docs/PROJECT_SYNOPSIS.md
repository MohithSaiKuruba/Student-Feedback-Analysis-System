# Project Synopsis: Student Feedback Analysis System

## Problem statement
Course feedback can be difficult to review consistently when ratings are collected manually. This project stores numeric feedback and summarizes course satisfaction patterns.

## Objectives
1. Collect anonymous course ratings.
2. Validate inputs and store data in a relational database.
3. Calculate course-wise and question-wise averages and counts.
4. Visualize rating distributions and export aggregate summaries.
5. Reduce identification risk by suppressing small groups and not publishing comments.

## Scope and roles
Respondents submit ratings; a project administrator configures the app and reviews aggregate reports. Features include course selection, four rating questions, optional comment, MySQL, Flask APIs, CSV export, Pandas/NumPy and Matplotlib charts.

## Technology
Python, Flask, MySQL, Pandas, NumPy, Matplotlib, HTML, CSS.

## Assumptions
Courses/questions are configured in advance. Ratings are integers from 1–5. One submitted form creates four rating records. Counts refer to rating answers rather than unique respondents. Synthetic data can be used for demonstration.

## Expected outcome
A working website, SQL schema, API, CSV export, charts, setup documentation and demonstration plan.

## Limitations
The group threshold reduces but does not eliminate identification risk. Comments may contain personal information. Production use needs authentication, CSRF protection, HTTPS and retention policies. Ratings are subjective and descriptive; they do not establish causation or objectively measure teaching quality.
