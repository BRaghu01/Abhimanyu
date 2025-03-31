// Mobile menu toggle
const mobileMenu = document.getElementById('mobile-menu');
const navLinks = document.getElementById('nav-links');

mobileMenu.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Recipe generation demo
const recipes = [
    {
        name: "Surplus Veggie Stir Fry",
        ingredients: [
            "2 bell peppers (surplus)",
            "1 zucchini (surplus)",
            "1 cup mushrooms (expiring soon)",
            "2 tbsp soy sauce",
            "1 tbsp sesame oil",
            "2 cloves garlic",
            "1 tsp ginger",
            "2 cups cooked rice"
        ],
        steps: [
            "Chop all vegetables into bite-sized pieces",
            "Heat sesame oil in a wok or large pan",
            "Add minced garlic and ginger, sauté for 30 seconds",
            "Add vegetables and stir fry for 5-7 minutes",
            "Add soy sauce and cook for 1 more minute",
            "Serve over cooked rice"
        ]
    },
    {
        name: "Leftover Pasta Primavera",
        ingredients: [
            "2 cups cooked pasta (leftover)",
            "1 cup mixed vegetables (surplus)",
            "1/4 cup cream (expiring soon)",
            "2 tbsp butter",
            "1/4 cup grated parmesan",
            "1 clove garlic",
            "Salt and pepper to taste"
        ],
        steps: [
            "Melt butter in a pan and sauté garlic for 30 seconds",
            "Add vegetables and cook until tender",
            "Stir in cream and bring to a simmer",
            "Add cooked pasta and toss to coat",
            "Sprinkle with parmesan and serve"
        ]
    },
    {
        name: "Fruit Surplus Smoothie Bowl",
        ingredients: [
            "1 banana (overripe)",
            "1/2 cup berries (surplus)",
            "1/2 cup yogurt (expiring soon)",
            "1 tbsp honey",
            "2 tbsp granola",
            "1 tsp chia seeds"
        ],
        steps: [
            "Blend banana, berries and yogurt until smooth",
            "Pour into a bowl and drizzle with honey",
            "Top with granola and chia seeds",
            "Serve immediately"
        ]
    }
];

const recipeCard = document.querySelector('.recipe-card');
const generateBtn = document.getElementById('generateRecipe');

generateBtn.addEventListener('click', function() {
    // Add animation class
    recipeCard.classList.remove('animate');
    
    // After a short delay, update the recipe and re-animate
    setTimeout(() => {
        const randomRecipe = recipes[Math.floor(Math.random() * recipes.length)];
        
        // Update recipe content
        document.querySelector('.recipe-header h3').textContent = randomRecipe.name;
        
        const ingredientsList = document.querySelector('.recipe-ingredients ul');
        ingredientsList.innerHTML = '';
        randomRecipe.ingredients.forEach(ingredient => {
            const li = document.createElement('li');
            li.textContent = ingredient;
            ingredientsList.appendChild(li);
        });
        
        const stepsList = document.querySelector('.recipe-steps ol');
        stepsList.innerHTML = '';
        randomRecipe.steps.forEach(step => {
            const li = document.createElement('li');
            li.textContent = step;
            stepsList.appendChild(li);
        });
        
        // Re-add animation class
        recipeCard.classList.add('animate');
    }, 300);
});

// Animation on scroll
function animateOnScroll() {
    const featureCards = document.querySelectorAll('.feature-card');
    const techLogos = document.querySelectorAll('.tech-logo');
    const modelCards = document.querySelectorAll('.model-card');
    const recipeCard = document.querySelector('.recipe-card');
    
    featureCards.forEach((card, index) => {
        const cardPosition = card.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (cardPosition < screenPosition) {
            setTimeout(() => {
                card.classList.add('animate');
            }, index * 100);
        }
    });
    
    techLogos.forEach((logo, index) => {
        const logoPosition = logo.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (logoPosition < screenPosition) {
            setTimeout(() => {
                logo.classList.add('animate');
            }, index * 100);
        }
    });
    
    modelCards.forEach((card, index) => {
        const cardPosition = card.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (cardPosition < screenPosition) {
            setTimeout(() => {
                card.classList.add('animate');
            }, index * 100);
        }
    });
    
    // Animate recipe card
    const recipePosition = recipeCard.getBoundingClientRect().top;
    const recipeScreenPosition = window.innerHeight / 1.3;
    
    if (recipePosition < recipeScreenPosition) {
        recipeCard.classList.add('animate');
    }
}

// Initialize animations on load
window.addEventListener('load', animateOnScroll);

// Add scroll event listener
window.addEventListener('scroll', animateOnScroll);