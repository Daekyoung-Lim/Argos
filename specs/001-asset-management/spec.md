# Feature Specification: Company Asset Management

**Feature Branch**: `001-asset-management`  
**Created**: 2026-03-04  
**Status**: Draft  

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Employee Asset Self-Survey (Priority: P1)

Employees need to verify their assigned company assets without physical visits from the asset manager by taking a photo of the asset sticker.

**Why this priority**: It solves the primary bottleneck of manual asset tracking, directly reducing the time and geographical constraints of asset surveys. This is the core MVP feature for employees.

**Independent Test**: Can be fully tested by an employee logging in, viewing their assigned asset, uploading a photo of a valid asset sticker, and seeing the asset status update to verified.

**Acceptance Scenarios**:

1. **Given** an employee is viewing an assigned asset in the app, **When** they upload a photo of the asset sticker containing the correct 10-digit code with valid metadata (location within 3km, taken within 48h), **Then** the system marks the asset as successfully surveyed.
2. **Given** an employee uploads an asset photo, **When** the location metadata is outside the 3km radius of the expected location, **Then** the system rejects the survey and displays an error message regarding the invalid location.
3. **Given** an employee uploads an asset photo, **When** the time metadata indicates the photo is older than 48 hours, **Then** the system rejects the survey and displays an error message about the expired timestamp.
4. **Given** an employee uploads an asset photo, **When** the extracted 10-digit code does not exactly match the asset's database code, **Then** the system rejects the survey and notifies the user of a code mismatch.

---

### User Story 2 - Admin NL Asset Query and Export (Priority: P1)

Asset managers need to quickly find information about assets and employees using natural language, and export this data to Excel for reporting and communication.

**Why this priority**: It is the core MVP feature for admins, providing them with immediate visibility into asset statuses without needing complex dashboard filtering logic.

**Independent Test**: Can be fully tested by an admin logging in, typing a natural language question (e.g., "Show me all employees who haven't verified their assets"), viewing the tabular results, and downloading them as an Excel file.

**Acceptance Scenarios**:

1. **Given** an admin is using the chatbot interface, **When** they ask a question about asset status in natural language, **Then** the system displays the correct data matching their request in a tabular format.
2. **Given** the chat interface displays query results, **When** the admin clicks the export button, **Then** the system downloads an Excel file containing the exact records shown in the UI.

---

### User Story 3 - Role-based Login and Access (Priority: P1)

The system must differentiate between general employees and asset managers to present the appropriate MVP features to each.

**Why this priority**: Essential security and routing mechanism to ensure employees can only survey their own assets and only admins can query the entire database.

**Independent Test**: Can be fully tested by authenticating as an employee and confirming the admin chatbot is inaccessible, and vice versa.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user, **When** they navigate to the app, **Then** they are prompted to log in.
2. **Given** a user logs in with Employee credentials, **When** they access the system, **Then** they are routed to their personal asset list and cannot access the admin chatbot.
3. **Given** a user logs in with Admin credentials, **When** they access the system, **Then** they are routed to the admin chatbot and management tools.

### Edge Cases & Assumptions

- **Missing Metadata**: What happens when a photo lacks location or time metadata? The system will reject the survey and prompt the user to enable device location services or retake the photo.
- **Blurry Photos**: How does the system handle photos where the code is illegible? It fails the extraction and asks the user to retake the photo clearly.
- **Ambiguous Admin Queries**: What happens when an admin asks a query that cannot be mapped to database fields? The chatbot will request clarification or a rephrased question.
- **Assumed Auth**: Standard session-based or token-based authentication is sufficient for the MVP.
- **Lifecycle Management Excluded**: Asset lifecycle events (provisioning, deprecation, transfer, return) are deliberately excluded from the MVP scope as per requirements.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a secure authentication mechanism separating 'Employee' and 'Admin' roles.
- **FR-002**: System MUST allow Employees to view a list of company assets currently assigned to them.
- **FR-003**: System MUST provide an interface for Employees to capture or upload a photo of an asset's sticker to perform a self-survey.
- **FR-004**: System MUST extract identifying text (specifically a 10-digit asset code) from the uploaded image.
- **FR-005**: System MUST extract location (GPS coordinates) and timestamp metadata from the uploaded image.
- **FR-006**: System MUST validate the survey by ensuring the extracted code exactly matches the database, the location is within a 3km radius of the expected location, and the time is within 48 hours of the current time.
- **FR-007**: System MUST provide a chatbot interface for Admins to submit natural language queries regarding assets and personnel.
- **FR-008**: System MUST translate natural language queries into accurate database structural queries to retrieve and display the results.
- **FR-009**: System MUST allow Admins to export the resulting conversational data into a downloadable Excel (.xlsx) file.

### Key Entities

- **User**: Represents a person in the system. Attributes: ID, Role, Name, Email.
- **Asset**: Represents a trackable company item. Attributes: 10-digit Code, Assigned User ID, Expected Location, Validation Status.
- **Survey Record**: Represents a self-survey attempt. Attributes: Record ID, Asset Code, Uploaded Image, Extracted Code/Location/Time, Pass/Fail Status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully complete an asset self-survey upload process in under 2 minutes.
- **SC-002**: Text extraction correctly identifies legible 10-digit asset codes from photos 95% of the time.
- **SC-003**: System accurately applies the 3km/48h constraints 100% of the time when valid metadata is present.
- **SC-004**: Admin natural language queries return logically correct and syntactically valid data for standard reporting use cases at least 90% of the time.
- **SC-005**: Excel generation and download of up to 10,000 queried records completes in under 5 seconds.
