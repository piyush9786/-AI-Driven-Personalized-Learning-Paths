// ======= Sample Class Data =======
const classes = [
    {
      name: "Programming in C++",
      instructor: "Alice Johnson",
      type: "Coding",
      schedule: "08:00 - 09:30",
      days: ["Monday", "Wednesday", "Friday"],
      enrolled: 2,
      capacity: 5,
      level: "Beginner",
      room: "Lab A"
    },
    {
      name: "DSA Mastery",
      instructor: "James Stewart",
      type: "Coding",
      schedule: "10:00 - 11:30",
      days: ["Tuesday", "Thursday"],
      enrolled: 5,
      capacity: 5,
      level: "Advanced",
      room: "Lab B"
    },
    {
      name: "Web Dev Basics",
      instructor: "Sophia Lin",
      type: "Frontend",
      schedule: "13:00 - 14:30",
      days: ["Monday", "Wednesday"],
      enrolled: 3,
      capacity: 6,
      level: "Intermediate",
      room: "Studio Web"
    }
  ];
  
  // ======= DOM Mount Function =======
  function renderClassRows() {
    const table = document.querySelector(".class-table");
  
    classes.forEach(cls => {
      const row = document.createElement("div");
      row.className = "class-row";
  
      const daysText = cls.days.join(", ");
      const fillPercent = Math.round((cls.enrolled / cls.capacity) * 100);
      const tagClass = cls.level.toLowerCase();
      const status = cls.enrolled >= cls.capacity ? "Full" : "Active";
  
      row.innerHTML = `
        <div>
          <strong>${cls.name}</strong>
          <br/><small>by ${cls.instructor}</small>
        </div>
        <div>${cls.type}</div>
        <div>
          <i class="fas fa-clock"></i> ${cls.schedule}
          <br/>
          <i class="fas fa-calendar-day"></i> ${daysText}
        </div>
        <div>
          <i class="fas fa-users"></i> ${cls.enrolled}/${cls.capacity}
          <div class="capacity-bar">
            <div style="width: ${fillPercent}%; background-color: ${
              fillPercent === 100 ? "#ff6b6b" : "#00ffe0"
            }"></div>
          </div>
        </div>
        <div>
          <span class="tag ${tagClass}">${cls.level}</span>
        </div>
        <div class="status ${status === "Full" ? "full" : "active"}">${status}</div>
      `;
  
      table.appendChild(row);
    });
  }
  
  // ======= Init on DOM Load =======
  document.addEventListener("DOMContentLoaded", () => {
    renderClassRows();
  });
  

  // ======= Click Glow Effect =======
document.addEventListener("click", (e) => {
    const row = e.target.closest(".class-row");
    if (row) {
      row.classList.add("clicked");
      setTimeout(() => {
        row.classList.remove("clicked");
      }, 600); // Duration of the glow animation
    }
  });
  