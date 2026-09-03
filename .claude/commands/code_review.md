Perform a structured code review.

Review the supplied file(s) and evaluate:

## Functionality
- Does the code meet the stated purpose?

## Code Quality
- Clear and readable code
- Appropriate naming conventions
- No duplicated logic

## Error Handling
- Exceptions handled appropriately
- Edge cases considered

## Logging
- Uses logger instead of print
- Meaningful log messages

## Performance
- Unnecessary loops or computations
- Inefficient Spark/DataFrame operations

## Security
- No hardcoded secrets
- Proper input validation

## Testing
- Missing unit tests
- Missing edge-case coverage

## Output Format

### Critical Issues

### Major Issues

### Minor Issues

### Recommendations

Code to review:
{{args}}