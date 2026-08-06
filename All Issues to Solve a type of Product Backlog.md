(Model Specific Issues) Model Related Changes Required or For Security Reasons.
* Candidate, Constituency, Election and other Data deletion after the end of election (discard of data)
* Inserting Specific Parties, needed or not think about that, if necessary or important add, if not add as ENUM Values can also extend the ENUM or Remove Values from ENUM, or if Model or Object Creation important do that.
* Voters List will be the same, won't change, addition can be allowed but no modification, deletion only when the user dies. (Re-Fetching data each-time and inserting it is a tedious process, rather fetch data but with comparison if it exists then don't insert but check for deceased value if it exists then discard that entry, if it doesn't exists then do insert, and check for deceased value before insertion.
* All check and issues clarifying, Checks include if election or candidate or some other object exists or not, and what if it doesn't what if some other issue occur, what if couldn't create, what if voter.has\_voted\_na is True but vote didn't get casted because of internet issue, all issues, needs more thinking to find more basic issues and solve them.
* Candidate Name and Party Name (Party Name Label so that TTS can read that aloud) displayed along with Party Symbol, Symbol must have labels so that the TTS can read it aloud for the blind user.
* Candidates can't be created before creating Constituencies, Solution is that Constituencies are created dynamically for Candidates when candidates are inserted, so that we don't have to manually create constituencies.
* Proper Usage of Polling station which is not being used, Proper design of Election Model so that Each election can have multiple elections for each Assembly Type, We don't have to create elections for each Assembly Manually.
* Both Ballot Boxes Creation on the Creation of Polling Station Automatically, so that we don't have to create Manually.
* Vote Calculations Dynamically (It can also be static only show at the end of Election), After the Election Ends A Proper Report for all Candidates for each Constituency, for each assembly, if a person is Trying to get a vote, for a specific, Constituency and at some other place too and for NA and PA too, calculations for each separately, and If there is a scenario where we have to calculate the total sum of votes for a candidates across different polling stations then total sum from all Ballot Boxes for that Specific Candidate.
* When a New Election Starts All Voters voter.has\_voted\_na and voter.has\_voted\_pa Value Assigned to be False for each election. and once the value is inserted it must be locked up so no changes could happen to it in any way possible, for a more secure E-Voting System.
* Reports for Each Election, for Each Polling Station, For Each Ballot Box (Both NA and PA), for Each Constituency, and For Each Candidate, for a more better visual understanding for vote casting and more better reports.
* Voters would vote in each polling station rather than like the current design where vote is casted directly in the ballot boxes first the polling station then that specific box then vote cast.
* Application of verification by Mother's Name of a Voter (Optional for now) or any other Form (Face, Fingerprint) (Optional Too for now Not Decided)

(File Upload System and Model Related Tasks) New File upload system for the ECP so they can Easily add Candidates and Polling station etc.
* Constituences Addition by ECP, How would it be Added, Automatic creation of constituencies when a list if fetched from the file that the ecp inputs, for easier creation and management of constituences.
* Respective Polling Stations fetched from the file, to assign polling station and creation of ballot boxes according to the given constituencies. (Polling station data fetched and Created according to the respective constituencies, if constituencies are not there they would be fetched first and polling station creation would trigger the creation of it's repective ballot boxes.)
* Fetching data of candidates from the same file as above that the ecp provides to create candidates. and assign then to their respective constituency.

(Decorators Sessions and Cookies) Issues and Things related to Session Handling and management and Login and verification or Decorators related to them.
* Proper Usage of @login\_required and @voter\_required decorators for views, for a secure login, logout and session handling.
* Proper session handling with more precision and perfection.
* @crsf\_exempt decorator meaning and usage
* cookies and session perfection, further thinking required. when to logout, and when not to. when two tabs on the same browser happens what to do then, same pc but different browsers then what solution for many more session related issues, find the issues (important, not found all issues yet further thinking required)

(Things to Understand) Things That caught my eye and needs to be understood, if required for the project would use them if not, self learning.
* what are tests/test_app.py and other tests.py files and how to properly use them.
* venv file clearing of unnecessary downloaded libraries and other cache etc.
* more better urls for my Django app so that the urls tells the story and it is more precise and accurate.
* What is app.py file what's the usage and how to properly use it.
* After Both Vote Casted Logout Automatically with a message to tell the blind that both vote has been casted.
* Automatically shift to the other Vote, For example if The Voter just casted Vote for National Assembly, It should Automatically shift to the Provincial Assembly Vote casting for Ease, and vice Versa, and if both are casted Automatic Logout with a Message (The Above Feature)
* Understand the concept of polling station in an area, and the number of constituencies each polling station can have.

(TTS and STT) Things, issues and Task related to TTS and STT for accessibility, Better UX and Usability.
* Proper TTS for each page, Label for each part so more easily accessible, and the TTS can read it with ease for the users.
* Proper TTS application regarding everything.
* Removing of All the STT Buttons at the end of project.
* More Better STT and Proper Application of it.
* When Voter is Prompted with Questions what mode of answer is best? Voice (Three Options: Full Said Sentences, Specific Words, Numbering) or Specific Keyboard Buttons For Example SpaceBar, Medium Size button, or Number Wise button pressing, or Special Buttons that are specifically designed for Blind People.

(UI and UI Related Tasks) Tasks and Issues Related to More Better UI, Animations, Grading, Smooth Transitions and Messages.
* Messages disappear after a specific time interval, and appear and disappear with cool and smooth transitions and a more appealing UI for messages.
* A more Better UI, Buttons, Colors, Font, Grading if possible, Visually Appealing, Names (what names still figuring out?), and messages (success, error or any other) better everything.
* A good transition from one screen to another, each screen transition must be smooth so that it feels good. Not important because blind people, but better for a good presentation.
* TTS based UI for easy access.
* A Good Transition from Normal Contrast to High Contrast

(Documentation Related Tasks)
* Re Write Or Change/Modify Details with the new understanding of the Project
* Modiify the Sprint Details.
* Modifiy the User Stories, Requirements, Sponsers or Stake Holders.
* Re Creation of Data Models. 
* Creation of C4 Models according to the new found Project Concept.
* Product Backlog Management.
* Tasks Division.
* Proper Tracking and Creation of Tasks.
* 
* 
* 
* 

