const tableBody = document.getElementById("members-table-body");

members.forEach(member => {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>
      <div class="member-info">
        <img src="${member.image}" alt="${member.name}" class="avatar">
        <div>
          <strong>${member.name}</strong><br>
          ${member.email}
        </div>
      </div>
    </td>
    <td>
      <i class="fas fa-envelope"></i> ${member.email}<br>
      <i class="fas fa-phone"></i> ${member.phone}
    </td>
    <td>${member.plan}</td>
    <td><i class="fas fa-calendar-alt"></i> ${member.joined}</td>
    <td><span class="status ${member.status.toLowerCase()}">${member.status}</span></td>
    <td>${member.lastVisit}</td>
    <td><i class="fas fa-ellipsis-v"></i></td>
  `;
  tableBody.appendChild(row);
});
