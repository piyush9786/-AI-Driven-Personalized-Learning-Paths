let questions = [
    {
      numb: 1,
      question: "What does SQL stand for?",
      answer: "Structured Query Language",
      options: [
        "Stylish Question Language",
        "Stylesheet Query Language",
        "Statement Question Language",
        "Structured Query Language"
      ]
    },
    {
      numb: 2,
      question: "What is the full form of DBMS?",
      answer: "Database Management System",
      options: [
        "Database Maintenance System",
        "Database Model System",
        "Database Management System",
        "Data Management Storage"
      ]
    },
    {
      numb: 3,
      question: "Which of the following is a relational database management system?",
      answer: "MySQL",
      options: [
        "MongoDB",
        "MySQL",
        "Redis",
        "Cassandra"
      ]
    },
    {
      numb: 4,
      question: "What is normalization in databases?",
      answer: "The process of organizing data to reduce redundancy",
      options: [
        "The process of encrypting data for security",
        "The process of organizing data to reduce redundancy",
        "The process of merging tables in the database",
        "The process of indexing data for faster search"
      ]
    },
    {
      numb: 5,
      question: "What does the ACID property in a database ensure?",
      answer: "Atomicity, Consistency, Isolation, Durability",
      options: [
        "Authentication, Consistency, Integration, Durability",
        "Atomicity, Consistency, Isolation, Durability",
        "Atomicity, Consistency, Information, Durability",
        "Access Control, Consistency, Integration, Durability"
      ]
    },
    {
      numb: 6,
      question: "What is a foreign key in a database?",
      answer: "A key used to link two tables together",
      options: [
        "A unique key in a table",
        "A key that represents the primary key of another table",
        "A key used to link two tables together",
        "A key that indexes data in a table"
      ]
    },
    {
      numb: 7,
      question: "What is a primary key?",
      answer: "A field or combination of fields that uniquely identifies a record in a table",
      options: [
        "A key that stores passwords",
        "A field or combination of fields that uniquely identifies a record in a table",
        "A key that links a table with another table",
        "A key that indexes rows for fast searching"
      ]
    },
    {
      numb: 8,
      question: "What is a join in SQL?",
      answer: "A method of combining rows from two or more tables based on a related column",
      options: [
        "A method of combining rows from two or more tables based on a related column",
        "A type of query that retrieves data from one table",
        "A method for deleting rows from a table",
        "A function used to compute aggregate values"
      ]
    },
    {
      numb: 9,
      question: "What is a deadlock in a database?",
      answer: "A situation where two or more transactions are blocked indefinitely due to mutual dependency",
      options: [
        "A situation where a transaction is delayed",
        "A situation where data is not accessible temporarily",
        "A situation where two or more transactions are blocked indefinitely due to mutual dependency",
        "A situation where the system crashes due to heavy load"
      ]
    },
    {
      numb: 10,
      question: "Which of the following is a NoSQL database?",
      answer: "MongoDB",
      options: [
        "Oracle",
        "MySQL",
        "MongoDB",
        "PostgreSQL"
      ]
    },
    // Complex DBMS Questions
    {
      numb: 11,
      question: "What is the difference between inner join and outer join?",
      answer: "An inner join returns only the rows where there is a match in both tables, while an outer join returns all rows from one table and matched rows from the other",
      options: [
        "An inner join returns all rows from both tables, while an outer join returns only matched rows",
        "An inner join returns only the rows where there is a match in both tables, while an outer join returns all rows from one table and matched rows from the other",
        "An inner join is faster than an outer join",
        "An inner join can be used for multiple tables, while outer join works for two tables only"
      ]
    },
    {
      numb: 12,
      question: "What is the purpose of an index in a database?",
      answer: "To speed up the retrieval of rows from a table",
      options: [
        "To make data retrieval slower",
        "To speed up the retrieval of rows from a table",
        "To delete records from a table",
        "To organize data in alphabetical order"
      ]
    },
    {
      numb: 13,
      question: "What is the difference between a clustered and non-clustered index?",
      answer: "A clustered index sorts and stores the data rows in the table based on the index key, while a non-clustered index stores the index separately from the data rows",
      options: [
        "A clustered index sorts and stores the data rows in the table based on the index key, while a non-clustered index stores the index separately from the data rows",
        "A clustered index is slower than a non-clustered index",
        "A clustered index can only be used on one column, while non-clustered indexes can be used on multiple columns",
        "A clustered index uses more memory than a non-clustered index"
      ]
    },
    {
      numb: 14,
      question: "What is normalization and why is it important?",
      answer: "Normalization is the process of organizing data to reduce redundancy and improve data integrity. It helps avoid anomalies and ensures consistency.",
      options: [
        "Normalization is the process of backing up data to avoid loss",
        "Normalization is the process of organizing data to reduce redundancy and improve data integrity. It helps avoid anomalies and ensures consistency.",
        "Normalization is the process of creating more indexes for faster queries",
        "Normalization is the process of encrypting sensitive data"
      ]
    },
    {
      numb: 15,
      question: "What is the use of a stored procedure in a DBMS?",
      answer: "A stored procedure is a set of SQL queries that can be stored and executed on the database server for repeated use",
      options: [
        "A stored procedure is a backup mechanism for data",
        "A stored procedure is a set of SQL queries that can be stored and executed on the database server for repeated use",
        "A stored procedure is used to store and manage database indexes",
        "A stored procedure is used for creating database tables"
      ]
    },
    {
      numb: 16,
      question: "What is the difference between a transactional and analytical database?",
      answer: "A transactional database is optimized for handling real-time data and transactions, while an analytical database is designed for complex queries and analysis",
      options: [
        "A transactional database is designed for data warehousing, while an analytical database handles live transactions",
        "A transactional database is optimized for handling real-time data and transactions, while an analytical database is designed for complex queries and analysis",
        "A transactional database can store more data than an analytical database",
        "A transactional database is used for database security, while an analytical database focuses on performance"
      ]
    },
    {
      numb: 17,
      question: "What is denormalization and why might it be used?",
      answer: "Denormalization is the process of combining tables to reduce the number of joins in queries. It is used to improve query performance at the cost of redundancy",
      options: [
        "Denormalization is the process of encrypting data for security",
        "Denormalization is the process of combining tables to reduce the number of joins in queries. It is used to improve query performance at the cost of redundancy",
        "Denormalization is the process of distributing data across different servers for scalability",
        "Denormalization is the process of creating indexes on all columns"
      ]
    },
    {
      numb: 18,
      question: "What is a trigger in a database?",
      answer: "A trigger is a set of SQL statements that automatically executes in response to certain events on a table or view",
      options: [
        "A trigger is used to store database queries",
        "A trigger is a set of SQL statements that automatically executes in response to certain events on a table or view",
        "A trigger is used to update the structure of a table",
        "A trigger is used for securing the database"
      ]
    },
    {
      numb: 19,
      question: "What is a schema in a database?",
      answer: "A schema is the structure that defines the organization of data, including tables, fields, relationships, and constraints",
      options: [
        "A schema is a tool for backing up data",
        "A schema is the structure that defines the organization of data, including tables, fields, relationships, and constraints",
        "A schema is the process of creating indexes on tables",
        "A schema is a software tool used to query the database"
      ]
    },
    {
      numb: 20,
      question: "What is the difference between SQL and NoSQL databases?",
      answer: "SQL databases are relational, structured, and use a predefined schema, while NoSQL databases are non-relational, flexible, and handle unstructured data",
      options: [
        "SQL databases are relational, structured, and use a predefined schema, while NoSQL databases are non-relational, flexible, and handle unstructured data",
        "SQL databases handle unstructured data, while NoSQL databases use structured schemas",
        "SQL databases are used for cloud-based applications, while NoSQL databases are for local storage",
        "SQL databases are slow for large datasets, while NoSQL databases are faster"
      ]
    }
  ];
  