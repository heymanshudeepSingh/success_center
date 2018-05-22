# Django - CAE Home App

## Description

A group of Django Apps to function as the "core" for future CAE Center projects.

Intended to be as general as possible.

## Usage Notes

### Initial Set Up

* On first time use, you will need to go into **settings/local_env** and copy **env.example.py** to **env.py**.
    * **Dev Mode** - Can probably leave file as is, if using SQLite. Otherwise, edit env file as desired.
    * **Production Mode** - Default env definitely isn't production ready. Will require modificaitons for stability
    and security.
* Make sure to run migrations to set up initial database schema.

### Front End

* Title Tag Template:
    * The title is in format of **[ Page | App | Site ]**, which seems to be the standard that Google, Stack Overflow,
    Django, and other major sites currently go by.
    * To be as generic as possible, the "Site" part of the title is set to default as "CAE Center". Where appropriate,
    this should be overridden with the website name (CAEWeb, West, etc).

* Main Nav and Subnav Menu Format:
    ```
    <li><a href="">Main Item 1</a></li>
    <li><a href="">Main Item 2</a></li>
    <li>
        <a href="">Main Item 3</a></li>
        <ul>
            <li><a href="">SubItem Item 1</a></li>
            <li><a href="">SubItem Item 2</a></li>
            <li><a href="">SubItem Item 3</a></li>
        </ul>
    </li>
    ```

### Back End

* User model separation:
    * The user model is split into two parts:
        * **User** - Contains fields relevant to authentication.
        * **Profile** - A one-to-one (User-correlated) model, which contains all other non-auth values.
