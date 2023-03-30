# Educational project.
Contains several independent projects.

===============================================================

Project 0: secondary files

    wait.py - Wait(ms) function implementation
    const.py - filename variables

===============================================================

Project 1: Endless cycle that reads lines from a text file

Description:
Script for endless reading of search phrases from a text file.
Implemented continuation of reading from the point of stop.

Project structure:

    main_txt.py - main executable,
    queries.txt - search phrases text file;
    queries_for_test.txt - mini text file for test;

===============================================================

Project 2: text file server

Description:
Server for editing a text file.
Management uses front-end and routes Flask.

Project structure:

    server_for_txt.py - main executable,
    front-end - app/templates/index.html

http://127.0.0.1:5080 - servers host/port

===============================================================

Project 3: PostgreSQL database server

Description:
Server for editing a PostgreSQL database.
Management uses front-end and routes Flask.

Project structure:

    server_db.py - main executable,
    front-end - app/templates/index_DB.html

Additional:

    app/models.py - description of database tables
    script_settings_db.py - script for writing settings to "settings_cycle" Database table
    script_request_db.py - script for writing request to "google_req" Database table
    script_print_db.py - script to print "result_info" Database table

http://127.0.0.1:8000 - servers host/port

===============================================================

Project 4: Endless cycle that reads queries from a PostgreSQL database

Description: 
Initial reading of settings from "settings_cycle" Database table.
Reading the list of text queries from "google_req" Database table.
Generating a list of answers from a Google search.
Writing results to "result_info" Database table.
Implemented continuation of reading from the point of stop.
No front-end.

Project structure:

    main_db.py - main executable

===============================================================

Project 5: Two queue from RabbitMQ (async pika)

Description:
Three-process analogue of "main_DB" (starter.py + worker.py + 
saver.py) using the two RabbitMQ queue.
No front-end.

Project structure:

    starter.py - get initial settings, get queries from DB usign mask "status.
        Change status and send queries to 'request_queue' RabbitMQ queue.
    worker.py - get queries from 'request_queue' RabbitMQ queue,
        parsing and send result parsing to 'result_queue' RabbitMQ queue.
    saver.py - get result from 'result_queue' RabbitMQ queue, save result
        in to database and back change status queries.

Additional:
    
    script_status_db.py - working with error queries. Change status "work"
        on status "not_work" for all queries.
    script_delete_db.py - delete all info from "result_info" table DB,
        reset autoincrement id from "result_info" table DB.

===============================================================

Project 0: secondary files

    script_argparse.py - script for learning "argparse" analisator,
        incl print/delete all info from selected table.

===============================================================
