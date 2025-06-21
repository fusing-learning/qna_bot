# UAT Test Cases - Task 5.2: Document Listing Implementation

## Test Environment Setup

**Prerequisites:**
1. FastAPI backend running on `http://localhost:8000`
2. Admin UI running on `http://localhost:8502`
3. At least 4-5 test documents uploaded to the system

**To start the environment:**
```bash
# Terminal 1 - Start API server
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m uvicorn src.app.api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Start Admin UI
source venv/bin/activate
streamlit run src/ui/admin.py --server.port 8502
```

---

## Test Case 1: Basic Document Listing Display

**Objective:** Verify that the document list page displays all uploaded documents with correct metadata

**Steps:**
1. Open browser and navigate to `http://localhost:8502`
2. From the sidebar, select "📋 Document List"
3. Observe the main document listing area

**Expected Results:**
- [ ] Page displays "📋 Document List" header
- [ ] Shows total document count (e.g., "Showing 4 of 4 documents")
- [ ] Each document displays:
  - [ ] Original filename in bold
  - [ ] Title and area information
  - [ ] Document ID and file type
  - [ ] Upload date
  - [ ] View and Delete buttons
- [ ] No error messages displayed

**Test Data Requirements:** At least 2-3 documents with different areas (HR, IT, Operations, etc.)

---

## Test Case 2: Document Metadata Display

**Objective:** Verify that all document metadata is correctly displayed

**Steps:**
1. Navigate to Document List page
2. Locate a document with complete metadata (title, description, area)
3. Click the "View" button for that document
4. Review the expanded details section

**Expected Results:**
- [ ] Document details expand in an accordion/expander
- [ ] All metadata fields are displayed:
  - [ ] Original Filename
  - [ ] Title
  - [ ] Description
  - [ ] Area/Category
  - [ ] File Size (formatted, e.g., "1.2 KB")
  - [ ] File Type
  - [ ] Upload Date (formatted)
  - [ ] Version number
  - [ ] File Path
- [ ] "Hide Details" button appears and functions
- [ ] Details can be collapsed by clicking "Hide Details"

---

## Test Case 3: View Button Functionality

**Objective:** Test the view button toggle behavior

**Steps:**
1. Navigate to Document List page
2. Click "View" button for Document A
3. Verify details expand
4. Click "View" button for Document B (while A is still expanded)
5. Click "Hide Details" for Document A
6. Refresh the page
7. Click "View" for Document A again

**Expected Results:**
- [ ] Clicking "View" expands document details
- [ ] Multiple documents can have details expanded simultaneously
- [ ] "Hide Details" button collapses the details
- [ ] View state is maintained during page interactions
- [ ] After page refresh, all details are collapsed (fresh state)

---

## Test Case 4: Individual Document Delete Functionality

**Objective:** Test the delete confirmation workflow

**Steps:**
1. Navigate to Document List page
2. Note the current total document count
3. Click "Delete" button for a test document
4. Observe the confirmation dialog
5. Click "Cancel" in the confirmation
6. Click "Delete" button again for the same document
7. Click "Confirm" in the confirmation dialog
8. Verify the document is deleted

**Expected Results:**
- [ ] Clicking "Delete" shows confirmation warning message
- [ ] Confirmation shows document filename
- [ ] "Confirm" and "Cancel" buttons appear
- [ ] Clicking "Cancel" dismisses confirmation without deleting
- [ ] Clicking "Confirm" deletes the document
- [ ] Success message appears: "Document deleted!"
- [ ] Document disappears from the list
- [ ] Total document count decreases by 1
- [ ] Page refreshes automatically

**⚠️ Note:** Use a test document that you don't need for other tests

---

## Test Case 5: Bulk Selection and Actions

**Objective:** Test the bulk selection and deletion functionality

**Steps:**
1. Navigate to Document List page
2. Verify at least 3 documents are available
3. Check the checkbox next to 2 documents
4. Click "Delete Selected" button
5. Click "Cancel Bulk Delete"
6. Select 2 documents again
7. Click "Delete Selected"
8. Click "Confirm Bulk Delete"

**Expected Results:**
- [ ] Individual checkboxes appear for each document
- [ ] Selected documents are tracked
- [ ] "Delete Selected" button becomes active when documents are selected
- [ ] Bulk delete confirmation shows number of documents to delete
- [ ] "Cancel Bulk Delete" cancels the operation
- [ ] "Confirm Bulk Delete" deletes all selected documents
- [ ] Success message shows count of deleted documents
- [ ] Selected documents disappear from list
- [ ] Total count updates correctly

**⚠️ Note:** Use test documents that you don't need for other tests

---

## Test Case 6: Select All Functionality

**Objective:** Test the "Select All" checkbox functionality

**Steps:**
1. Navigate to Document List page
2. Ensure at least 3 documents are visible
3. Click "Select All" checkbox
4. Verify all individual checkboxes are selected
5. Uncheck one individual document checkbox
6. Observe the "Select All" checkbox state
7. Check "Select All" again

**Expected Results:**
- [ ] "Select All" checkbox selects all visible documents
- [ ] All individual checkboxes become checked
- [ ] Unchecking individual documents doesn't affect "Select All" state
- [ ] "Select All" can be used multiple times
- [ ] Selected documents are properly tracked for bulk actions

---

## Test Case 7: Area Filtering

**Objective:** Test document filtering by area/category

**Steps:**
1. Navigate to Document List page
2. Ensure you have documents in different areas (HR, IT, Operations, etc.)
3. Note the total document count
4. Select "HR" from the "Filter by Area" dropdown
5. Observe the filtered results
6. Select "IT" from the dropdown
7. Select "All" to clear the filter

**Expected Results:**
- [ ] Area filter dropdown contains all expected options
- [ ] Selecting an area shows only documents from that area
- [ ] Document count updates to show filtered count
- [ ] No documents message appears if no documents match filter
- [ ] Selecting "All" shows all documents again
- [ ] Pagination resets when filter changes

**Test Data Requirements:** Documents with different area values (HR, IT, Operations, Finance, etc.)

---

## Test Case 8: Pagination Functionality

**Objective:** Test pagination controls and page navigation

**Steps:**
1. Ensure you have at least 6 documents in the system
2. Navigate to Document List page
3. Set "Documents per page" to 2
4. Observe pagination controls
5. Click "Next ⏩" button
6. Click "Previous ⏪" button
7. Click "Last ⏭️" button
8. Click "First ⏮️"
9. Change "Documents per page" to 10

**Expected Results:**
- [ ] Pagination controls appear when needed
- [ ] Page information shows correctly (e.g., "Page 1 of 3")
- [ ] "Next" and "Last" buttons work correctly
- [ ] "Previous" and "First" buttons work correctly
- [ ] Buttons are disabled appropriately (First/Previous on page 1, Next/Last on last page)
- [ ] Changing page size updates the view
- [ ] Document count per page is respected
- [ ] Page navigation maintains filter settings

**Test Data Requirements:** At least 6 documents to test pagination

---

## Test Case 9: Error Handling

**Objective:** Test system behavior when API is unavailable

**Steps:**
1. Navigate to Document List page with API running
2. Stop the FastAPI server (Ctrl+C in terminal)
3. Refresh the Document List page
4. Try to click "View" on a document
5. Try to delete a document
6. Restart the API server
7. Refresh the page

**Expected Results:**
- [ ] When API is down, appropriate error messages appear
- [ ] "Failed to load documents" message shows
- [ ] View and Delete operations show error messages
- [ ] No crashes or unexpected behavior
- [ ] When API is restored, functionality returns to normal
- [ ] Error messages are user-friendly

---

## Test Case 10: Page Refresh and State Management

**Objective:** Test UI state management across page refreshes

**Steps:**
1. Navigate to Document List page
2. Set filter to "HR"
3. Set page size to 25
4. Navigate to page 2 (if available)
5. Select some documents with checkboxes
6. Refresh the browser page (F5)
7. Observe the page state

**Expected Results:**
- [ ] Filter selection is reset to "All"
- [ ] Page size resets to default (10)
- [ ] Page number resets to 1
- [ ] Document selections are cleared
- [ ] All expanded details are collapsed
- [ ] No error messages appear
- [ ] Document list loads correctly

---

## Test Case 11: Responsive UI Layout

**Objective:** Test UI layout with different amounts of data

**Steps:**
1. Test with no documents in system
2. Test with 1 document
3. Test with 10+ documents
4. Test with documents having very long titles/descriptions
5. Test with documents having no title/description (N/A values)

**Expected Results:**
- [ ] "No documents found" message when empty
- [ ] UI handles single document correctly
- [ ] UI handles many documents without layout issues
- [ ] Long text is handled gracefully (wrapping or truncation)
- [ ] "N/A" displays for missing optional fields
- [ ] Bulk actions section appears only when documents exist

---

## Test Summary Checklist

After completing all tests, verify:

- [ ] All basic functionality works as expected
- [ ] Document metadata is correctly displayed
- [ ] View and delete buttons function properly
- [ ] Bulk actions work correctly
- [ ] Filtering and pagination work
- [ ] Error handling is appropriate
- [ ] UI is responsive and user-friendly
- [ ] No crashes or unexpected behavior observed

## Reporting Issues

If any test fails, please document:
1. Test case number and name
2. Steps that failed
3. Expected vs actual result
4. Browser and version used
5. Any error messages in browser console (F12)
6. Screenshots if helpful

---

**Test Environment:** 
- Backend: http://localhost:8000
- Frontend: http://localhost:8502
- Date: [Fill in test date]
- Tester: [Fill in tester name]