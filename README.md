# 510_lab3
# How to Run
Open the terminal and run the following commands:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# What's include
app.py - main running application.  
.gitignore - tells Git which files or directories to ignore in a project.  
BostonHousing.csv - csv dataset for application.  
requirements.txt - list all the dependencies that the project needs to run correctly.  
README.md - includes the text info of the basic introduction of this GitHub Repository, how to run, what's included, lessons learned, questions / uncertainties.  

# Lesson Learned
During my journey of technical improvement, I effectively utilized sqlite3 to develop and implement data models, ensuring the correctness of the data structure and the consistency of data in the application. Using the Pydantic class, I was able to not only quickly construct basic forms but also enhance the interactivity and functionality of the user interface through its advanced features, such as filterable dropdown menus. Moreover, I gained valuable experience in adjusting database structures, particularly in how to handle practical issues during database upgrades. I found that to prevent errors related to non-existent columns during database updates, it is crucial to delete the old sqlite file first, a key step in ensuring the stable operation of the application.



# questions
1.How can version control for database schemas be effectively managed to minimize disruption in a production environment?
2.What are some best practices for automating the migration of data when database schemas change, especially when using tools like sqlite3 in small to medium-sized projects?
