let data = [];
let selectedIndex = -1;
let unsaved = false;

// 🔹 LOAD DATA FROM BACKEND
window.onload = loadData;

async function loadData() {
  try {
    let res = await fetch("https://admin-backend-a018.onrender.com/get-products");
    let json = await res.json();

    data = json.products || [];
    renderTable();

  } catch (err) {
    alert("Failed to load data");
    console.error(err);
  }
}

// 🔹 RENDER TABLE
function renderTable() {
  const tbody = document.querySelector("#productTable tbody");
  tbody.innerHTML = "";

  data.forEach((item, index) => {
    let name = item.name ?? "";
    let price = item.price ?? "";
    let img = item.images?.[0] ?? "";
    let desc = item.description ?? "";

    tbody.innerHTML += `
      <tr onclick="selectRow(${index})">
        <td>${name}</td>
        <td>${price}</td>
        <td>${img}</td>
        <td>${desc}</td>
      </tr>
    `;
  });
}

// 🔹 SELECT ROW
function selectRow(index) {
  selectedIndex = index;
  let item = data[index];

  document.getElementById("name").value = item.name ?? "";
  document.getElementById("price").value = item.price ?? "";
  document.getElementById("img").value = item.images?.[0] ?? "";
  document.getElementById("info").value = item.description ?? "";
  document.getElementById("category").value = item.category ?? "bestseller";
  document.getElementById("availability").value = item.availability ?? "in-stock";
}

// 🔹 CLEAR INPUTS
function clearInputs() {
  document.getElementById("name").value = "";
  document.getElementById("price").value = "";
  document.getElementById("img").value = "";
  document.getElementById("info").value = "";
  selectedIndex = -1;
}

// 🔹 ADD ITEM
function addItem() {
  if (!confirm("Add this product?")) return;

  let item = {
    id: Date.now(),
    name: document.getElementById("name").value,
    price: parseInt(document.getElementById("price").value) || 0,
    category: document.getElementById("category").value,
    availability: document.getElementById("availability").value,
    images: [document.getElementById("img").value],
    description: document.getElementById("info").value
  };

  data.unshift(item);
  markUnsaved();
  renderTable();
}

// 🔹 UPDATE ITEM
function updateItem() {
  if (selectedIndex < 0) {
    alert("Select a product first");
    return;
  }

  if (!confirm("Update this product?")) return;

  let item = data[selectedIndex];

  item.name = document.getElementById("name").value;
  item.price = parseInt(document.getElementById("price").value) || 0;
  item.category = document.getElementById("category").value;
  item.availability = document.getElementById("availability").value;
  item.images = [document.getElementById("img").value];
  item.description = document.getElementById("info").value;

  markUnsaved();
  renderTable();
}

// 🔹 DELETE ITEM
function deleteItem() {
  if (selectedIndex < 0) {
    alert("Select a product first");
    return;
  }

  if (!confirm("Delete this product?")) return;

  data.splice(selectedIndex, 1);
  selectedIndex = -1;

  markUnsaved();
  renderTable();
}

// 🔹 MOVE UP
function moveUp() {
  if (selectedIndex <= 0) return;

  [data[selectedIndex], data[selectedIndex - 1]] =
  [data[selectedIndex - 1], data[selectedIndex]];

  selectedIndex--;
  markUnsaved();
  renderTable();
}

// 🔹 MOVE DOWN
function moveDown() {
  if (selectedIndex >= data.length - 1) return;

  [data[selectedIndex], data[selectedIndex + 1]] =
  [data[selectedIndex + 1], data[selectedIndex]];

  selectedIndex++;
  markUnsaved();
  renderTable();
}

// 🔹 SYNC TO BACKEND
async function syncData() {
  if (!unsaved) {
    alert("No changes to sync");
    return;
  }

  if (!confirm("Send all changes to GitHub?")) return;

  try {
    await fetch("https://admin-backend-a018.onrender.com/update-products", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ products: data })
    });

    alert("Synced 🚀");
    unsaved = false;
    document.getElementById("status").innerText = "✅ Synced";

  } catch (err) {
    alert("Sync failed");
    console.error(err);
  }
}

// 🔹 MARK UNSAVED
function markUnsaved() {
  unsaved = true;
  document.getElementById("status").innerText = "⚠ Unsaved";
}