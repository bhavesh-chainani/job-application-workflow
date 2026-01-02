# Email Processing Improvements

## Problems Solved

### 1. **Status Overwriting Issue** ✅
**Problem**: When processing emails, a rejection email would show "Rejected", but then processing the original application email would change it back to "Applied".

**Solution**: 
- Implemented a **status hierarchy system** that prevents backward status changes
- Status can only move forward: `Applied` → `Recruiter Screen` → `Interview` → `Offer`
- Can move to final status from any stage: `Applied` → `Rejected`
- Cannot move backward from final status: `Rejected` → `Applied` ❌
- Status hierarchy: `Applied (0)` < `Recruiter Screen (1)` < `Interview (2)` < `Rejected/Ghosted/Dropped (3)` < `Offer (4)`

### 2. **Email Repetition** ✅
**Problem**: Same emails were being processed multiple times, creating duplicate entries.

**Solution**:
- Added `processed_emails` table to track which emails have been processed
- Emails are checked **before** processing to skip already-processed ones
- Each email is marked as processed after successful parsing
- Even failed emails are marked to prevent infinite retry loops

### 3. **Better Email Matching** ✅
**Problem**: Application email (Jan 1) and rejection email (Jan 6) weren't being linked together.

**Solution**:
- Enhanced matching algorithm that considers:
  - **Company name** (must match)
  - **Job title** (at least 2 common words, or 1 word if title is short)
  - **Application date** (within 30 days)
- Improved LLM prompt to better identify related emails
- Automatic linking of related emails to the same application entry
- Status updates are applied to the original application, not creating duplicates

### 4. **Performance Improvements** ✅
- Skip already-processed emails early (before fetching email details)
- Only process new emails or emails that need updates
- Reduced redundant API calls and LLM processing

## How It Works Now

### Email Processing Flow

1. **Check if processed**: Before fetching email details, check `processed_emails` table
   - If processed → Skip
   - If not processed → Continue

2. **Parse email**: Use LLM to extract job information

3. **Match existing applications**: 
   - Check for exact match (same email_id)
   - Check for related application (company + role + date match)
   - Check for fuzzy match (company + similar role)

4. **Update or Create**:
   - If match found → Update existing application (respecting status hierarchy)
   - If no match → Create new application
   - Mark email as processed

5. **Status Updates**:
   - Only allow forward progress in status
   - Final statuses (Rejected, Ghosted, Dropped, Offer) cannot be overwritten by earlier statuses
   - Can upgrade between final statuses if higher priority (Rejected → Offer ✅)

## Database Schema Changes

### New Table: `processed_emails`
```sql
CREATE TABLE processed_emails (
    email_id VARCHAR(255) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_id INTEGER REFERENCES job_applications(id)
);
```

### New Indexes
- `idx_company_job` on `(company, job_title)` for faster matching

## Status Hierarchy Rules

| Current Status | Can Update To | Cannot Update To |
|---------------|---------------|------------------|
| Applied | Recruiter Screen, Interview, Rejected, Ghosted, Dropped, Offer | - |
| Recruiter Screen | Interview, Rejected, Ghosted, Dropped, Offer | Applied |
| Interview | Rejected, Ghosted, Dropped, Offer | Applied, Recruiter Screen |
| Rejected | Offer | Applied, Recruiter Screen, Interview |
| Ghosted | Offer | Applied, Recruiter Screen, Interview |
| Dropped | Offer | Applied, Recruiter Screen, Interview |
| Offer | - | Any other status |

## Example Scenarios

### Scenario 1: Application + Rejection
1. **Jan 1**: Application confirmation email → Creates entry: `Company A - Software Engineer - Applied`
2. **Jan 6**: Rejection email → Matches existing entry → Updates: `Company A - Software Engineer - Rejected` ✅
3. **Jan 7**: Re-run process_emails → Skips both emails (already processed) ✅

### Scenario 2: Status Progression
1. **Jan 1**: Application → `Applied`
2. **Jan 5**: Recruiter email → `Recruiter Screen` ✅
3. **Jan 10**: Interview invite → `Interview` ✅
4. **Jan 15**: Rejection → `Rejected` ✅
5. **Jan 20**: Re-process application email → Status stays `Rejected` (cannot go backward) ✅

### Scenario 3: Multiple Applications Same Company
1. **Jan 1**: Application for "Software Engineer" → Creates entry
2. **Jan 2**: Application for "Product Manager" → Creates new entry (different role)
3. **Jan 5**: Rejection for "Software Engineer" → Updates first entry only ✅

## Migration Notes

The new `processed_emails` table will be created automatically on first run. Existing emails in `job_applications` will be marked as processed automatically, so you won't lose any data.

If you want to re-process all emails, you can truncate the `processed_emails` table:
```sql
TRUNCATE TABLE processed_emails;
```

## Testing

To test the improvements:
1. Run `process_emails.py` - it should process new emails
2. Run it again - it should skip already-processed emails
3. Check that status updates respect the hierarchy
4. Verify that related emails (application + rejection) are linked together




