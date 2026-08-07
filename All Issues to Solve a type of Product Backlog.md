Section A: (Model Specific Issues) Model Related Changes Required or For Security Reasons.
A1. * Candidate, Constituency, Election and other Data deletion after the end of election (discard of data)
A2. * Inserting Specific Parties, needed or not think about that, if necessary or important add, if not add as ENUM Values can also extend the ENUM or Remove Values from ENUM, or if Model or Object Creation important do that.
A3. * Voters List will be the same, won't change, addition can be allowed but no modification, deletion only when the user dies. Re-Fetching data each-time and inserting it is a tedious process, rather fetch data but with comparison if it exists then don't insert but check for deceased value if it exists then discard that entry, if it doesn't exists then do insert, and check for deceased value before insertion.
A4. * All check and issues clarifying, Checks include if election or candidate or some other object exists or not, and what if it doesn't what if some other issue occur, what if couldn't create, what if voter.has_voted_na is True but vote didn't get casted because of internet issue, all issues, needs more thinking to find more basic issues and solve them.
A5. * Candidate Name and Party Name (Party Name Label so that TTS can read that aloud) displayed along with Party Symbol, Symbol must have labels so that the TTS can read it aloud for the blind user.
A6. * Candidates can't be created before creating Constituencies, Solution is that Constituencies are created dynamically for Candidates when candidates are inserted, so that we don't have to manually create constituencies.
A7. * Proper Usage of Polling station which is not being used, Proper design of Election Model so that Each election can have multiple elections for each Assembly Type, We don't have to create elections for each Assembly Manually. Both Ballot Boxes Creation on the Creation of Polling Station Automatically, so that we don't have to create Manually.
A8. * Vote Calculations Dynamically (It can also be static only show at the end of Election), After the Election Ends A Proper Report for all Candidates for each Constituency, for each assembly, if a person is Trying to get a vote, for a specific, Constituency and at some other place too and for NA and PA too, calculations for each separately, and If there is a scenario where we have to calculate the total sum of votes for a candidates across different polling stations then total sum from all Ballot Boxes for that Specific Candidate.
A9. * When a New Election Starts All Voters voter.has_voted_na and voter.has_voted_pa Value Assigned to be False for each election. and once the value is inserted it must be locked up so no changes could happen to it in any way possible, for a more secure E-Voting System.
A10. * Reports for Each Election, for Each Polling Station, For Each Ballot Box (Both NA and PA), for Each Constituency, and For Each Candidate, for a more better visual understanding for vote casting and more better reports.
A11. * Voters would vote in each polling station rather than like the current design where vote is casted directly in the ballot boxes first the polling station then that specific box then vote cast.
A12. * Application of verification by Mother's Name of a Voter (Optional for now) or any other Form (Face, Fingerprint) (Optional Too for now Not Decided)

Section B: (File Upload System and Model Related Tasks) New File upload system for the ECP so they can Easily add Candidates and Polling station etc.
B1. * Constituences Addition by ECP, How would it be Added, Automatic creation of constituencies when a list if fetched from the file that the ecp inputs, for easier creation and management of constituences.
B2. * Respective Polling Stations fetched from the file, to assign polling station and creation of ballot boxes according to the given constituencies. (Polling station data fetched and Created according to the respective constituencies, if constituencies are not there they would be fetched first and polling station creation would trigger the creation of it's repective ballot boxes.)
B3. * Fetching data of candidates from the same file as above that the ecp provides to create candidates. and assign then to their respective constituency.

Section C: (Decorators Sessions and Cookies) Issues and Things related to Session Handling and management and Login and verification or Decorators related to them.
C1. * Proper Usage of @login_required and @voter_required decorators for views, for a secure login, logout and session handling.
C2. * Proper session handling with more precision and perfection.
C3. * @crsf_exempt decorator meaning and usage
C4. * cookies and session perfection, further thinking required. when to logout, and when not to. when two tabs on the same browser happens what to do then, same pc but different browsers then what solution for many more session related issues, find the issues (important, not found all issues yet further thinking required)

Section D: (Things to Understand) Things That caught my eye and needs to be understood, if required for the project would use them if not, self learning.
D1. * what are tests/test_app.py and other tests.py files and how to properly use them.
D2. * venv file clearing of unnecessary downloaded libraries and other cache etc.
D3. * more better urls for my Django app so that the urls tells the story and it is more precise and accurate.
D4. * What is app.py file what's the usage and how to properly use it.
D5. * After Both Vote Casted Logout Automatically with a message to tell the blind that both vote has been casted.
D6. * Automatically shift to the other Vote, For example if The Voter just casted Vote for National Assembly, It should Automatically shift to the Provincial Assembly Vote casting for Ease, and vice Versa, and if both are casted Automatic Logout with a Message (The Above Feature)
D7. * Understand the concept of polling station in an area, and the number of constituencies each polling station can have.

Section E: (TTS and STT) Things, issues and Task related to TTS and STT for accessibility, Better UX and Usability.
E1. * Proper TTS for each page, Label for each part so more easily accessible, and the TTS can read it with ease for the users.
E2. * Proper TTS application regarding everything.
E3. * Removing of All the STT Buttons at the end of project.
E4. * More Better STT and Proper Application of it.
E5. * When Voter is Prompted with Questions what mode of answer is best? Voice (Three Options: Full Said Sentences, Specific Words, Numbering) or Specific Keyboard Buttons For Example SpaceBar, Medium Size button, or Number Wise button pressing, or Special Buttons that are specifically designed for Blind People.

Section F: (UI and UI Related Tasks) Tasks and Issues Related to More Better UI, Animations, Grading, Smooth Transitions and Messages.
F1. * Messages disappear after a specific time interval, and appear and disappear with cool and smooth transitions and a more appealing UI for messages.
F2. * A more Better UI, Buttons, Colors, Font, Grading if possible, Visually Appealing, Names of Voter, Candidates, Polling Station, Election , and messages (success, error or any other) better everything.
F3. * A good transition from one screen to another, each screen transition must be smooth so that it feels good. Not important because blind people, but better for a good presentation.
F4. * TTS based UI for easy access.
F5. * A Good Transition from Normal Contrast to High Contrast

Section G: (Documentation Related Tasks)
G1. * Re Write Or Change/Modify Details with the new understanding of the Project
G2. * Modiify the Sprint Details.
G3. * Modifiy the User Stories, Requirements, Sponsers or Stake Holders.
G4. * Re Creation of Data Models. 
G5. * Creation of C4 Models according to the new found Project Concept.
G6. * Product Backlog Management.
G7. * Tasks Division.
G8. * Proper Tracking and Creation of Tasks.