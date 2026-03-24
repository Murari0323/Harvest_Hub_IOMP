/**
 * HarvestHub — Premium Client-side JavaScript
 * =============================================
 * Scroll animations, typewriter, particles, counters, navbar effects.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Scroll-triggered fade/slide animations ─────────────
    var animatedElements = document.querySelectorAll('.fade-in, .slide-left, .slide-right');
    
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

        animatedElements.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        // Fallback: show all immediately
        animatedElements.forEach(function (el) {
            el.classList.add('visible');
        });
    }

    // ── 2. Navbar scroll effect ───────────────────────────────
    var navbar = document.getElementById('mainNavbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ── 3. Typewriter effect for hero subtitle ────────────────
    var typewriterEl = document.getElementById('typewriterText');
    if (typewriterEl) {
        var phrases = [
            'AI-driven platform connecting farmers directly with buyers.',
            'Smart crop recommendations • Price predictions • Zero middlemen.',
            'Empowering agriculture with machine learning.',
            'From farm to table — powered by technology.'
        ];
        var phraseIndex = 0;
        var charIndex = 0;
        var isDeleting = false;
        var typingSpeed = 45;

        function typeWriter() {
            var currentPhrase = phrases[phraseIndex];

            if (isDeleting) {
                typewriterEl.textContent = currentPhrase.substring(0, charIndex - 1);
                charIndex--;
                typingSpeed = 25;
            } else {
                typewriterEl.textContent = currentPhrase.substring(0, charIndex + 1);
                charIndex++;
                typingSpeed = 45;
            }

            if (!isDeleting && charIndex === currentPhrase.length) {
                typingSpeed = 2500; // Pause at end
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                phraseIndex = (phraseIndex + 1) % phrases.length;
                typingSpeed = 300;
            }

            setTimeout(typeWriter, typingSpeed);
        }

        // Start after a small delay
        setTimeout(typeWriter, 800);
    }

    // ── 4. Counter animation ──────────────────────────────────
    var counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        var counterObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var counter = entry.target;
                    var target = parseInt(counter.getAttribute('data-target'));
                    var duration = 2000;
                    var startTime = null;

                    function animateCount(timestamp) {
                        if (!startTime) startTime = timestamp;
                        var progress = Math.min((timestamp - startTime) / duration, 1);
                        // Ease-out cubic
                        var eased = 1 - Math.pow(1 - progress, 3);
                        var current = Math.floor(eased * target);
                        counter.textContent = current.toLocaleString() + (target >= 100 && counter.closest('.stat-item').querySelector('p').textContent.includes('%') ? '' : '+');
                        
                        if (progress < 1) {
                            requestAnimationFrame(animateCount);
                        } else {
                            counter.textContent = target.toLocaleString() + '+';
                        }
                    }

                    requestAnimationFrame(animateCount);
                    counterObserver.unobserve(counter);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(function (c) {
            counterObserver.observe(c);
        });
    }

    // ── 5. Floating particles (hero section) ──────────────────
    var particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        var particleCount = 25;
        for (var i = 0; i < particleCount; i++) {
            var particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDuration = (8 + Math.random() * 12) + 's';
            particle.style.animationDelay = (Math.random() * 8) + 's';
            particle.style.width = (3 + Math.random() * 6) + 'px';
            particle.style.height = particle.style.width;
            particle.style.opacity = (0.2 + Math.random() * 0.4).toString();

            // Vary colors between gold and green
            if (Math.random() > 0.5) {
                particle.style.background = 'rgba(212, 168, 67, 0.5)';
            } else {
                particle.style.background = 'rgba(29, 185, 84, 0.4)';
            }

            particlesContainer.appendChild(particle);
        }
    }

    // ── 6. Confirm before deleting a crop ─────────────────────
    document.querySelectorAll('.delete-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to delete this crop?')) {
                e.preventDefault();
            }
        });
    });

    // ── 7. Auto-dismiss flash alerts after 5 seconds ──────────
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ── 8. Quantity validation on cart ─────────────────────────
    var qtyInput = document.getElementById('quantity');
    if (qtyInput && qtyInput.hasAttribute('max')) {
        qtyInput.addEventListener('change', function () {
            var max = parseFloat(this.getAttribute('max'));
            if (parseFloat(this.value) > max) {
                this.value = max;
                alert('Maximum available quantity is ' + max + ' kg');
            }
            if (parseFloat(this.value) <= 0) {
                this.value = 1;
            }
        });
    }

    // ── 9. Live search filter on marketplace ──────────────────
    var searchInput = document.getElementById('searchInput');
    var cropGrid = document.getElementById('cropGrid');
    if (searchInput && cropGrid) {
        searchInput.addEventListener('input', function () {
            var query = this.value.toLowerCase();
            cropGrid.querySelectorAll('.crop-card-col').forEach(function (col) {
                var text = col.textContent.toLowerCase();
                col.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    // ── 10. Parallax effect on hero ───────────────────────────
    var heroSection = document.getElementById('heroSection');
    if (heroSection) {
        window.addEventListener('scroll', function () {
            var scrolled = window.scrollY;
            if (scrolled < 800) {
                heroSection.style.backgroundPositionY = (scrolled * 0.4) + 'px';
            }
        });
    }

    // ── 11. Smooth button ripple effect ───────────────────────
    document.querySelectorAll('.btn-success, .btn-info').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            var ripple = document.createElement('span');
            ripple.style.cssText = 'position:absolute;border-radius:50%;background:rgba(255,255,255,0.3);width:0;height:0;transform:translate(-50%,-50%);animation:rippleEffect 0.6s ease-out;pointer-events:none;';
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            
            var rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';
            
            this.appendChild(ripple);
            setTimeout(function () { ripple.remove(); }, 600);
        });
    });

    // Ripple keyframes injection
    if (!document.getElementById('rippleStyles')) {
        var style = document.createElement('style');
        style.id = 'rippleStyles';
        style.textContent = '@keyframes rippleEffect{to{width:300px;height:300px;opacity:0;}}';
        document.head.appendChild(style);
    }
});
