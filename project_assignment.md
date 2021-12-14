# Patient Monitoring Client/Server Project, Modified (Fall 2021)

## Overview
The final project in this class will require you to leverage the
industry-standard skills you've learned during this semester to design a 
Patient Monitoring
System with a patient-side client and a
server/database that allows patient data to be uploaded and stored on the
server for later ad-hoc and continuous monitoring.

It is expected that you will follow proper professional software
development and design conventions taught in this class, including:
* git feature-branch workflow
* continuous integration
* unit testing
* PEP8
* docstrings


## Functional Specifications
### Patient-side GUI Client
At a minimum, your patient-side GUI client should provide a __graphical__ user 
interface with the following functionality:
  + Allow the user to enter a patient name.
  + Allow the user to enter a patient medical record number.
  + Allow the user to select an ECG data file from the local computer.  This
  ECG data should then be analyzed for heart rate in beats per minute, display 
  the resulting heart rate in the GUI, and display an image of the ECG 
  trace in the interface.
  + Upon user command, issue a RESTful API request to your server to upload
  whatever information is entered above.  The interface should only allow this
  request to be made if at least a medical record number has been entered.
  Data to upload should include the medical record number, patient name, 
  measured heart rate, and ECG image.  If an item was not
  selected or added, it does not need to be uploaded.  
  + The user should have the ability to update any of this information in the
  GUI and upload the new information to the server.
  + The user should have the ability to start entry of new patient information
  and have the information previously shown for the old patient be removed from
  the GUI.
  + The user should have the ability, from a dropdown list,  to choose an 
  existing patient medical record number from the database.  Upon selection, the
  patient's name and MRN should be displayed in the GUI input boxes so further
  data entry for that patient could be made.

For the ECG analysis of heart rates, please use your existing ECG analysis 
code module, and modify it with a function that your GUI can call to execute
your code to do the 
analysis.  The ECG data files will be the same test files from the ECG Analysis
assignment.  This ECG code will not be re-evaluated and does not need unit
tests (although it will still need to pass PEP-8 testing).  The only evaluation
that will be made is that you call this function correctly from the GUI code
and receive the heart rate back correctly.  You don't need the correct heart
rate (i.e., whatever heart rate your code measured for the original ECG 
assignment will be considered the correct heart rate for this assignment).  
   

### Cloud Server
At a minimum, your server should be a cloud-based web service running on your 
virtual machine that exposes a well-crafted RESTful API that will implement 
the tasks needed by the client as described above and outlined here:

* Accept uploads from the patient-side client that will include, at a minimum,
the medical record number.  The upload may also include a name, 
and/or heart rate & ECG image.
* Communicate with and utilize a persistent database that will store the above
uploaded data for retrieval at a future time.  
* When a heart rate and ECG image are received, the date and time of receipt 
should be stored with the data.
* If the upload contains a medical record number not already found in the 
database, a new entry should be made for that patient, and the information 
  sent with the request stored in this new record.  
* If the upload contains a medical record number already found in the database,
any heart rate/ECG image sent with the request should be
added to the existing information. If a patient name is also sent, it should 
update the existing name in the database.
* Accept requests from the client to retrieve the following
information from the database and download it to the client:
  + a list of available patient medical record numbers
  + the name for a specific patient specified by MRN
  __Note__: The above list does not imply that you must have one route for
  each of those items.  Just make sure your server provides the needed 
  services.
* Provide any other services as needed for the client to perform its needed
functions.

**Note**: The GUI should only make requests to the server and should not make 
contact with the database.  All database functions should be handled from the
server.  If the GUI needs to interact with the database, it should do it by
making requests of the server. 

## Deliverables
* All project code for the GUI client, server, and tests (in the form of a 
  tagged GitHub repository).  All code should be well documented with docstrings.
* A detailed `README` describing the final performance and state of your
  project.  This should include a basic instruction manual for your GUI 
  clients, an API reference guide for your server, and a description of your
  database structure.
* A video demonstration will not be required.  Please just ensure that your
  README instructions are adequate to understand the use of the GUI.
* The URL of your deployed web service in your`README.md` (e.g., 
  `vcm-11111.vm.duke.edu:5000`)

<!--## Recommended Datasets
Your project may utilize some existing databases of images (or you can choose to
use your own images).  Here are some example datasets that you can access for
this project:

* <https://medpix.nlm.nih.gov/home>
* http://www.vision.caltech.edu/Image_Datasets/Caltech101/
* <https://www.cs.toronto.edu/~kriz/cifar.html>
* https://github.com/beamandrew/medical-data
* Over 13000 annotated skin lesion images are available from the International
  Skin Imaging Collaboration (ISIC) project:
  https://isic-archive.com. 
-->
## Grading

The following is a partial list of aspects on which the project that will be 
graded.

* Git Repository
  + Commits are discrete, logical change sets
  + Feature-branch workflow
* Software best practices
  + Modularity of software code
  + Handling and raising exceptions as needed
  + Language convention and style (PEP8)
  + Docstrings for all functions
* Testing and CI
  + Unit test coverage of all functions (except Flask handler and GUI calls)
  + GitHub Actions CI passing build
* Cloud-based Web Service
  + RESTful API Design 
  + Validation Logic 
  + Returning proper error codes
  + Robust deployment on virtual machine 
* Proper use of a database 
* User interface functionality
* Robust README

## Links of Interest
* [Image Toolbox](../Resources/image_toolbox.md)
* [Tkinter Intro](../Lectures/intro_to_gui.md)
* [Images in Tkinter](../Resources/tkinter_images.md)
* [Tkinter Toolbox](../Resources/tkinter_toolbox.md) 

## Q & A and Clarifications
As questions are raised and clarifications made, I will include those here:

**Testing of Image Toolbox Code**

Question: Does the "image toolbox" code that I shared need to be tested with unit 
tests.  The answer is **yes**.  Ideally, 
all of your code will have a unit test.  As we have seen so far this semester, 
some code can be problematic to have a unit test for (such as the flask 
handlers or GUI code).  But, this image code can be tested.

I have added some sample tests and advice on how to devise such tests on the 
class GitHub repo page [Resources/image_toolbox.md](https://github.com/dward2/BME547/blob/master/Resources/image_toolbox.md#testing-toolbox-code).

Please, if you are having any trouble designing a unit test for any of your 
functions, please open a GitHub issue with a link to the function you are 
trying to test and I will help you design an appropriate test.  And, if you 
have any question about the information on this webpage, please let me know.
