const members = [
  {
    name: "Smit Joshi",
    email: "SmitJoshi@gmail.com",
    phone: "9876543211",
    plan: "Premium",
    joined: "6 April 2025",
    status: "2 days ago",
    lastVisit: "2 days ago",
    image: "/static/images/profile_pic_default.webp"
  },
  {
    name: "Om Murhekar",
    email: "OmMurhekar@gmail.com",
    phone: "1234567890",
    plan: "Basic",
    joined: "09 April 2025",
    status: "Active",
    lastVisit: "Today",
    image: "/static/images/profile_pic_default.webp"
  },
  {
    name: "Snehal Yadav",
    email: "SnehalYadav@gmail.com",
    phone: "9876543210",
    plan: "Basic",
    joined: "09 April 2025",
    status: "Active",
    lastVisit: "Today",
    image: "/static/images/profile_pic_default.webp"
  },
  {
    name: "Piyush Shinde",
    email: "PiyushShinde@gmail.com",
    phone: "9876543213",
    plan: "Premium",
    joined: "25 March 2025",
    status: "a week ago",
    lastVisit: "Today",
    image: "/static/images/profile_pic_default.webp"
  },
  {
    name: "Saurav Yadav",
    email: "SauravYadav@gmail.com",
    phone: "9876543215",
    plan: "Basic",
    joined: "03 April 2025",
    status: "6 days ago",
    lastVisit: "Today",
    image: "/static/images/profile_pic_default.webp"
  },
  {
    name: "Soham Dhavale",
    email: "SohamDhavale@gmail.com",
    phone: "9876543267",
    plan: "Premium",
    joined: "04 April 2025",
    status: "3 days ago",
    lastVisit: "Today",
    image: "/static/images/profile_pic_default.webp"
  },
  {
    name: "Kunal Bondale",
    email: "KunalBondalee@gmail.com",
    phone: "9876543232",
    plan: "Basic",
    joined: "05 April 2025",
    status: "3 days ago",
    lastVisit: "Today",
    image: "/static/images/profile_pic_default.webp"
  },
];

function addMember() {
  const input = document.getElementById("memberNameInput");
  const name = input.value.trim();
  if (name !== "") {
    const list = document.getElementById("memberList");
    const listItem = document.createElement("li");
    listItem.textContent = name;
    list.appendChild(listItem);
    input.value = "";
  }
}
