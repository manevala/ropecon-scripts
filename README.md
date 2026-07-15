# ropecon-scripts

Helper scripts for organising Ropecon.

## source/dimensions/add_dimension.py

Add a program dimension and/or dimension values to Kompassi via the Kompassi GraphQL API. To run, you'll need a Kompassi
user with program admin privileges.

## source/dimensions/set_grouping_dimensions.py

Set values of the grouping dimension on program items based on answers of a non-dimension 'grouping' field on the 
corresponding program offer. To run, you'll need a Kompassi
user with program admin privileges.

## source/dimensions/set_registration_dimensions.py

Set values of the registration dimension on program items based on answers of a non-dimension 'registration' field on the 
corresponding program offer. To run, you'll need a Kompassi user with program admin privileges.

## source/program_helpers/send_program_helper_invites.py

Send invites to program helpers given on the program offer form. To run, you'll need a Kompassi
user with program admin privileges.

## source/tickets/send_tickets.py

Send tickets to a given list of people, with optionally marking them paid. To run, you'll need a Kompassi
user with ticket admin privileges.

You can find an example input Excel in data/example_ticket_orders.xlsx. The fields in the xlsx file should be, in order
* First name of recipient
* Last name of recipient (note that Kompassi needs both first and last names to create an order)
* Email to send tickets to 
* Id of ticket product in Kompassi (this is an integer)
* Language code for the ticket email (FI or EN)
* Number of tickets to send in this order 

## source/perks/set_perks.py

Set volunteer / program host perks (== ticket type and food voucher count) based on an Excel file. 
Does not override perks so that they become worse. For example, will not update a weekend ticket into a day ticket.
Requires a Kompassi user with involvement privileges.

You can find an example input Excel in data/example_perks.xlsx. The fields in the xlsx file should be, in order
* Email of user (the one used in their Kompassi account)
* 1 if the person should get a weekend ticket, 0 otherwise
* Food voucher count (integer), can be 0
