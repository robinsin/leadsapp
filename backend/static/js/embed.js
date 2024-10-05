(function() {
    const script = document.currentScript;
    const groupId = script.getAttribute('data-group-id');

    function renderForm(formStructure) {
        const form = document.createElement('form');
        form.id = 'lead-capture-form';

        formStructure.forEach(field => {
            const label = document.createElement('label');
            label.textContent = field.label;

            const input = document.createElement('input');
            input.type = field.type;
            input.name = field.id;
            input.required = field.required;

            form.appendChild(label);
            form.appendChild(input);
        });

        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit';
        form.appendChild(submitButton);

        form.addEventListener('submit', handleSubmit);

        script.parentNode.insertBefore(form, script);
    }

    function handleSubmit(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        fetch(`http://localhost:8000/api/ld-group/lead-groups/${groupId}/leads/`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert('Lead submitted successfully!');
            event.target.reset();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }

    fetch(`http://localhost:8000/api/ld-group/lead-groups/${groupId}/embed-form/`)
        .then(response => response.json())
        .then(data => renderForm(data.form_structure))
        .catch(error => console.error('Error:', error));
})();
