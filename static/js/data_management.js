// Data Management JavaScript

// Load available objects on page load
document.addEventListener('DOMContentLoaded', () => {
    loadObjects();
});

async function loadObjects() {
    try {
        const response = await fetch('/api/data/objects');
        const objects = await response.json();
        
        const selector = document.getElementById('objectSelector');
        selector.innerHTML = '<option value="">-- Select an object --</option>' +
            objects.map(obj => `<option value="${obj.name}">${obj.labelPlural}</option>`).join('');
    } catch (error) {
        console.error('Failed to load objects:', error);
    }
}

async function loadRecords() {
    const objectName = document.getElementById('objectSelector').value;
    if (!objectName) {
        document.getElementById('recordsCard').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/data/${objectName}/records?limit=50`);
        const data = await response.json();
        
        if (data.records && data.records.length > 0) {
            displayRecords(data.records, objectName);
            document.getElementById('recordCount').textContent = 
                `Showing ${data.records.length} of ${data.totalSize} records`;
            document.getElementById('recordsCard').style.display = 'block';
        } else {
            document.getElementById('recordsTable').innerHTML = '<p>No records found.</p>';
            document.getElementById('recordsCard').style.display = 'block';
        }
    } catch (error) {
        console.error('Failed to load records:', error);
        alert('Failed to load records: ' + error.message);
    }
}

function displayRecords(records, objectName) {
    const container = document.getElementById('recordsTable');
    
    if (records.length === 0) {
        container.innerHTML = '<p>No records found.</p>';
        return;
    }
    
    // Get field names (excluding attributes)
    const fields = Object.keys(records[0]).filter(key => key !== 'attributes');
    
    // Create table
    let html = '<table><thead><tr>';
    fields.forEach(field => {
        html += `<th>${field}</th>`;
    });
    html += '<th>Actions</th></tr></thead><tbody>';
    
    records.forEach(record => {
        html += '<tr>';
        fields.forEach(field => {
            let value = record[field];
            if (typeof value === 'object' && value !== null) {
                value = JSON.stringify(value);
            }
            html += `<td>${value || '-'}</td>`;
        });
        html += `<td>
            <button class="btn btn-sm btn-secondary" onclick="editRecord('${objectName}', '${record.Id}')">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteRecord('${objectName}', '${record.Id}')">Delete</button>
        </td></tr>`;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function showCreateDialog() {
    const objectName = document.getElementById('objectSelector').value;
    if (!objectName) {
        alert('Please select an object first');
        return;
    }
    
    const count = prompt('How many records would you like to create?', '10');
    if (count && parseInt(count) > 0) {
        createBulkRecords(objectName, parseInt(count));
    }
}

async function createBulkRecords(objectName, count) {
    const template = {};
    
    // Default templates for common objects
    if (objectName === 'Individual') {
        template.LastName = 'Person{i}';
        template.FirstName = 'Test';
    } else if (objectName === 'Contact') {
        template.LastName = 'Contact{i}';
        template.FirstName = 'Test';
    }
    
    try {
        const response = await fetch(`/api/data/${objectName}/bulk-create`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ count, template })
        });
        
        const result = await response.json();
        if (result.success) {
            alert(`Created ${result.created} records successfully!`);
            loadRecords();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Failed to create records: ' + error.message);
    }
}

async function deleteRecord(objectName, recordId) {
    if (!confirm('Are you sure you want to delete this record?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/data/${objectName}/${recordId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Record deleted successfully');
            loadRecords();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Failed to delete record: ' + error.message);
    }
}

function editRecord(objectName, recordId) {
    alert('Edit functionality coming soon! Record ID: ' + recordId);
}



