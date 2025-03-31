// Select the home wrapper to add the slide-out effect
const homeWrapper = document.querySelector('.home-wrapper');

// Register as Coach button click event
document.querySelector('.coach').addEventListener('click', function() {
    homeWrapper.classList.add('slide-out'); // Add the slide-out class
    setTimeout(function() {
        window.location.href = '../template/register_coach.html'; // Navigate to correct page after animation
    }, 300); // Delay to match the animation duration (0.3s)
});

// Register as Player button click event
document.querySelector('.player').addEventListener('click', function() {
    homeWrapper.classList.add('slide-out'); // Add the slide-out class
    setTimeout(function() {
        window.location.href = '../template/register_player.html'; // Navigate to correct page after animation
    }, 300); // Delay to match the animation duration (0.3s)
});
