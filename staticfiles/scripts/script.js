function filterEvents(filterType) {
    const events = document.querySelectorAll('.event');
    const today = new Date();

    events.forEach(event => {
        const eventDate = new Date(event.getAttribute('data-date'));
        event.style.display = 'block'; // Reset visibility

        if (filterType === 'upcoming' && eventDate < today) {
            event.style.display = 'none';
        } else if (filterType === 'past' && eventDate >= today) {
            event.style.display = 'none';
        }
    });
}