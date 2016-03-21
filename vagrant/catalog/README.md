<h1>Overview</h1>
This project contains the files necessary to run an online item catalog as described in FSND-Project 3.  I decided to leverage Twitter's Bootstrap library to handle the user interface; I've been very happy with it in the past, and have been waiting for an opportunity to try out its flyout modal menus.

From the course's preconfigured Vagrant VM, run the following commands to perform one-time initial DB setup
and launch the webserver:
    <ul>
    <li>(browse to the catalog project directory)</li>
    <li>python dal.py</li>
    <li>python catalog.py</li>
    </ul>

Once that is complete, follow along with the walkthrough below for a feature overview.

<h1>Overview: Basic Features</h1>

Open an HTML5-compliant browser (tested on Chrome) and head to http://localhost:5000.

The splash page (linked from the project branding in the top-left corner) shows a list of items that have been recently added or updated in the center of the screen.
You should see the four dummy items created by our database setup script.  Click any of the item names to be taken directly to their info pages.

On the item info page, you will see that the sidebar menu to the left automatically detects the active category and expands it to list all items in that category.  The numeric badges to the right of the category names also give an indicator of how many items exist without having to drill down into each category.

Click into another category on the sidebar menu and select another item.  The item viewer page and sidebar should reflect your new selection.

<h1>Overview: Advanced Features</h1>

All features covered so far are available whether or not a user is logged in.  To test the rest of the app, you'll need a Google account.

Click the "Log in" link in the top-right corner.  You will be redirected to the login page listing all available authentication sources (currently just Google+).  Click the "G+ Sign in" button and log in with your account.  You will see a few auth screens flicker by, then be redirected to the splash page.

Now that you're logged in, there are a few new features.  Your username is visible in the top-right corner (you can log out when the walkthrough is over by clicking on it).In the sidebar menu, you can create new categories and items.  Click the (add new category) button now.

You should see a popup menu asking for the new category's name.  Try to click "Confirm" without filling out the field; HTML5 form validation stops you, backed by additional data controls in the business logic layer.  Fill out a category name and click Confirm.

Your new category is now visible in the sidebar.  Congratulations!  It will look a bit different because this category "belongs" to your user account, unlike the two dummy categories which were created by fake users.  Click the gear icon to the right of your category's name in the sidebar, next to the item count (0).

You will see a popup menu allowing you to Update or Delete your category.  Try updating it first by setting a new name (which should be immediately reflected in the sidebar), then deleting it.

You should now be back on the splash screen with just the two dummy categories.  Click one of them in the sidebar, then the (add new item) link.

Just as before, you now get to create your own item.  All fields are required.  The category you had open is selected for convenience, but you can change that dropdown if you decide there is a better fit while typing it up.  Of special note is the ".jpg only" restriction on uploading pictures.  In addition to the form validators used here in the UI, the backend also inspects the file's contents with the imghdr library to ensure it actually contains valid JPEG data.

Create an item now by filling out the fields and clicking Confirm.  You should be redirected to the item viewer page you saw earlier.  Of note here is that we use Bootstrap's thumbnail styling to help display the image properly -- even with very large pictures, they should automatically be resized to avoid distorting the page.  Just as before when you made a category, there is a gear icon next to your item's name in the sidebar.  Click it now, then Update.

The item update form is a bit different than the others we've seen so far.  All of the fields are optional; if you leave anything blank here, the item will retain its existing values.  Update the item a few times -- rename it, move it to a different category, change its picture.  Note how the sidebar and item viewer page react intelligently as you make changes.

<h1>Endpoints</h1>

Two endpoints are available for exposing catalog data to external services.  The mandatory JSON endpoint is available at http://localhost:5000/catalog.json (validated against http://jsonlint.com/), and an additional Atom endpoint listing recent changes is available at http://localhost:5000/catalog.atom (validated against https://validator.w3.org/feed/#validate_by_input)



