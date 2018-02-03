# Gamers NBA CRUD App

---

### Project Summary
This project employs the Flask framework to develop a RESTful web application. SQLAlchemy a severless database is the persistent storage for data populated.
Authentication was guaranteed using OAuth2 to provide further CRUD functionality on the application. Facebook and Google Accounts authentication were used.


---

## Quick start
#### Requirements
- Python
- Virtual Box
- Vagrant

## Installations
### VirtualBox

VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

**Windows Note:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

## Fetch the Source Code and VM Configuration

**Windows:** Use the Git Bash program (installed with Git) to get a Unix-style terminal.  
**Other systems:** Use your favorite terminal program.

From the terminal, run:

    git clone https://github.com/judekuti/Gamers_NBA.git GamersNBA

This will give you a directory named **GamersNBA** complete with the source code for the flask application, a vagrantfile, and a bootstrap.sh file for installing all of the necessary tools. 

## Run the virtual machine!

Using the terminal, change directory to oauth (**cd GamersNBA**), then type **vagrant up** to launch your virtual machine.

## Running the GamersNBA App
Once it is up and running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.


Now that you have Vagrant up and running type **vagrant ssh** to log into your VM.  change to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains project.py, database_setup.py, and two directories named 'templates' and 'static'

Now type **python db_setup.py** to initialize the database.

Type **python gamersnba.py** to populate the database with restaurants and menu items. (Optional)

Type **python app.py** to run the Flask web server. In your browser visit **http://localhost:5000** to view the Gamers NBA app.  You should be able to view, add, edit, and delete menu players and franchises. Now you are a franchise owner :smiley:


## Get Google Client ID
- Visit[https://console.developers.google.com/Google](https://console.developers.google.com/Google)
- Sign up or Login if prompted
- Go to Credentials
- Select Create Crendentials > OAuth Client ID
- Select Web application
- Enter name 'Item-Catalog'
- Authorized JavaScript origins = 'http://localhost:5000'
- Authorized redirect URIs = 'http://localhost:5000/login' && 'http://localhost:5000/gconnect'
- Select Create
- Copy the Client ID and paste it into the data-clientid in login.html
- On the Dev Console Select Download JSON
- Rename JSON file to client_secrets.json
- Place JSON file in this item-catalog directory
- Run application using python app.py

#### Environment Set-Up
- Installation set-up require Unix-Style Terminal or Git Bash Terminal for windows
- Download VirtualBox [virtualbox.org](here)
- Install Vagrant [vagrantup.com](here)
    > Note to make a firewall exception or allow permissions for these downloads
- Check for successful download with `vagrant --version`
- Navigate into the 'vagrant' directory, run ```vagrant up```.
- SSH to the virtual machine with ```vagrant ssh```.

#### Run the program
1. Launch the VM:
    a. `vagrant up`
    b. `vagrant ssh`
2. Within the VM, navigate to `cd /vagrant`
3. Execute the database orm first with `python db_setup.py`
4. Populate the database with an initial set of data with `python gamersnba.py`
5. Execute the program with `python app.py`

---


## JSON Endpoints
 The following are open to the public:

franchise JSON: `/franchise/JSON`
    - Displays all franchises.

franchise/roster JSON: `'/franchise/<int:franchise_id>/roster/JSON'`
   - Displays the roster of a specific franchise

 Category Items JSON: `/franchise/<int:franchise_id>/roster/<int:player_id>/JSON`
   -Displays the profile of a specific player belonging to a specific franchise


## References
- [https://www.python-course.eu](https://www.python-course.eu/index.php)
- [http://www.sqlalchemy.org/](http://www.sqlalchemy.org/)
- [https://www.python-course.eu/index.php](https://www.python-course.eu/index.php)
- [http://flask.pocoo.org/](http://flask.pocoo.org/)

