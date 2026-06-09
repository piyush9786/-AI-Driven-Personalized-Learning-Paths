const subjects = [
    {
      name: "Python",
      description: "A beginner-friendly programming language used for web, automation, and data science.",
      whyLearn: [
        "Great for beginners due to simple syntax",
        "Widely used in data science and AI",
        "Has a massive ecosystem of libraries"
      ],
      advantages: [
        "Readable and concise code",
        "Cross-platform compatibility",
        "Strong community support"
      ],
      roadmap: [
        "Basics: Syntax, Variables, Data Types",
        "Control Structures & Functions",
        "OOP & Modules",
        "File Handling",
        "Libraries: NumPy, Pandas",
        "Web (Flask/Django) or ML (Scikit-learn)"
      ]
    },
    {
      name: "Java",
      description: "A popular object-oriented programming language used in Android and enterprise applications.",
      whyLearn: [
        "Strong job market demand",
        "Foundation for Android Development",
        "Widely used in backend systems"
      ],
      advantages: [
        "Platform independent via JVM",
        "Strong OOP principles",
        "Vast ecosystem (Spring, Hibernate)"
      ],
      roadmap: [
        "Basics: Syntax, Data Types",
        "OOP Concepts: Classes, Objects, Inheritance",
        "Collections & Exception Handling",
        "Multithreading & File I/O",
        "JDBC & Servlets",
        "Spring Framework"
      ]
    },
    {
      name: "C++",
      description: "A powerful language with low-level memory control, used in games, systems, and embedded software.",
      whyLearn: [
        "Improves understanding of memory and performance",
        "Used in high-performance systems and game development",
        "Builds strong programming fundamentals"
      ],
      advantages: [
        "Fast and efficient",
        "Supports both procedural and OOP",
        "Close to hardware"
      ],
      roadmap: [
        "Syntax & Data Types",
        "Control Structures",
        "Pointers and Memory Management",
        "OOP: Classes, Inheritance, Polymorphism",
        "STL (Standard Template Library)",
        "Projects & Practice"
      ]
    },
    {
      name: "DBMS",
      description: "Database Management Systems help manage, query, and structure data efficiently.",
      whyLearn: [
        "Essential for backend and data-centric apps",
        "Helps in data modeling and storage",
        "Foundation for SQL and NoSQL databases"
      ],
      advantages: [
        "Efficient data handling",
        "Ensures data consistency and security",
        "Scalable systems"
      ],
      roadmap: [
        "Database Models & Architecture",
        "ER Diagrams & Normalization",
        "SQL Queries",
        "Joins & Subqueries",
        "Transactions & Concurrency",
        "Indexing & NoSQL Basics"
      ]
    },
    {
      name: "OS",
      description: "Operating Systems manage computer hardware and software resources.",
      whyLearn: [
        "Core subject for understanding how computers work",
        "Helps in system-level and kernel development",
        "Essential for interviews and CS fundamentals"
      ],
      advantages: [
        "Understand process management",
        "File systems & memory concepts",
        "Networking basics"
      ],
      roadmap: [
        "Process & Thread Management",
        "Memory Management & Paging",
        "Deadlocks & Scheduling Algorithms",
        "File Systems",
        "I/O & Interrupts",
        "Security & Virtualization"
      ]
    },
    {
      name: "Networking",
      description: "Learn how data travels between computers, servers, and devices.",
      whyLearn: [
        "Fundamental for backend, DevOps, and security roles",
        "Improves understanding of internet protocols",
        "Important for cloud & distributed systems"
      ],
      advantages: [
        "Understand HTTP, TCP/IP, DNS",
        "Troubleshoot and configure networks",
        "Foundation for cybersecurity"
      ],
      roadmap: [
        "Basics of Networking",
        "OSI & TCP/IP Models",
        "IP Addressing & Subnetting",
        "Routing & Switching",
        "Protocols (DNS, DHCP, HTTP)",
        "Firewalls & VPNs"
      ]
    },
    {
      name: "DevOps",
      description: "DevOps bridges development and operations, emphasizing automation and CI/CD.",
      whyLearn: [
        "Helps deploy, monitor, and scale apps efficiently",
        "Demanded in cloud and agile teams",
        "Improves collaboration and automation"
      ],
      advantages: [
        "Faster delivery cycles",
        "Scalability and monitoring",
        "Strong job opportunities"
      ],
      roadmap: [
        "Linux & Shell Scripting",
        "Version Control (Git)",
        "CI/CD: Jenkins, GitHub Actions",
        "Docker & Kubernetes",
        "Monitoring: Prometheus, Grafana",
        "Cloud Providers: AWS, GCP basics"
      ]
    }
  ];
  
  // Inject into HTML
  const container = document.getElementById("subjects-container");
  
  subjects.forEach(subject => {
    const subjectSection = document.createElement("div");
    subjectSection.className = "subject";
  
    subjectSection.innerHTML = `
      <details>
        <summary><strong>${subject.name}</strong> - ${subject.description}</summary>
        <div style="padding: 1rem; margin-top: 0.5rem;">
          <h4>Why Learn:</h4>
          <ul>${subject.whyLearn.map(item => `<li>${item}</li>`).join('')}</ul>
  
          <h4>Advantages:</h4>
          <ul>${subject.advantages.map(item => `<li>${item}</li>`).join('')}</ul>
  
          <h4>Roadmap:</h4>
          <ol>${subject.roadmap.map(step => `<li>${step}</li>`).join('')}</ol>
        </div>
      </details>
      <hr style="margin: 1.5rem 0; border-color: #222;">
    `;
    
    container.appendChild(subjectSection);
  });
  