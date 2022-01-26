# Pantry Controller
#### Video Demo:  https://youtu.be/VzYC8vTVhwc
#### Description:

#### This is a web application that aims to simplify the management of your pantry and fridge. It allows you to log everything you buy and consumes, alerts you about stuff that is about to expire (3 days from the expiration date), and generates a shopping list for when you need to go shopping.

#### When you first get on the site, you will need to create an account and log in. After that you will be in the main page. Upon your first log in it will be empty, but as you add items you have in your pantry, they will show up in there. Also, the items that are about to expire will be displayed on a second table on top of the complete pantry table.

#### To Add items just fill all the boxes and click “add”. If you already have some items, they will be shown in a table below. The item box has a autocomplete function if you use the arrows on the keyboard and the list of all items will also display only items that match what you are typing.

#### On the remove tab you can remove items as you consume them. (This tab will be worked on and improved in the next few days)

#### The next tab is the default pantry, where you will need to log what items and how much of it you want to always have available. This will be used to generate the shopping list. Just fill the boxes and press ”add” to add a new or more of a item. You can also remove some of an item with the button “remove” or remove the item totally by clicking the “x” on the item itself.

#### The shopping list tab will display that you don’t need anything if you have enough of everything you added to the default pantry. In case you need something, a table will be displayed showing everything and how much you need, and you can click the download button to download a csv file with everything you need (will be changed to a pdf soon).

#### The files in the project are:
#### -	application.py: the backend logic of the hole application
#### -	helpers.py: Has the login validation function
#### -	requirements.txt: describes all the necessary libraries to build the project
#### -	Procfile: Is use to signalise to Heroku what the application is
#### -	storage.db: is the database I use during the development, when moved to Heroku, the database will be changed to postgress.db.
#### -	the statics folder has the small image that shows on the on the browser tab and the css file
#### -	the templates folder has the individual html for each page on the application, as well as the layout that generates the base for all other pages

#### On the database structuring I run in to a debate with myself, if I should create a table that had all items, a table with all users and a table that linked them booth. Even though that had the possibility of saving some space because you would have the same item multiple times, I think that the variety of available products, brands, names for the same product, miss spellings,… added with the space of having the linking table would make it not worth in terms of space, and it would add processing time in the querrys, which are very frequent

#### Also, the validation of if the boxes where correctly filed is all begging done server side. I plan on changing most of that to JS in the future.