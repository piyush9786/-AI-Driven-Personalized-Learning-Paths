// Function to add a task
function addTask() {
    const taskInput = document.getElementById('task-input');
    const taskList = document.getElementById('task-list');
    const taskCounter = document.getElementById('task-counter');
    const progressBar = document.getElementById('progress-bar');

    const taskName = taskInput.value;
    if (taskName === '') {
        alert('Please enter a task.');
        return;
    }

    // Create new task element
    const taskItem = document.createElement('li');
    taskItem.textContent = taskName;
    
    // Create a button to mark task as completed
    const completeButton = document.createElement('button');
    completeButton.textContent = 'Complete';
    completeButton.onclick = function() {
        taskItem.classList.toggle('completed');
        updateProgress();
    };

    // Append the button to the task item
    taskItem.appendChild(completeButton);
    taskList.appendChild(taskItem);
    
    // Clear input
    taskInput.value = '';
    
    // Update progress
    updateProgress();
}

// Function to update progress
function updateProgress() {
    const taskList = document.getElementById('task-list');
    const taskCounter = document.getElementById('task-counter');
    const progressBar = document.getElementById('progress-bar');
    
    const totalTasks = taskList.children.length;
    const completedTasks = document.querySelectorAll('.completed').length;

    const progress = (completedTasks / totalTasks) * 100;
    taskCounter.textContent = `${completedTasks} Tasks Completed`;
    progressBar.value = progress;
}
