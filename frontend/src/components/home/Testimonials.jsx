import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Quote } from 'lucide-react';

const Testimonials = () => {
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.3 });

  const testimonials = [
    {
      quote: "I saved 8,500 KES on my new Samsung phone by waiting for just two weeks after setting up a Thamani alert.",
      name: "David Kamau",
      product: "Samsung Galaxy S22",
      savings: "8,500 KES"
    },
    {
      quote: "As a student, every shilling counts. Thamani helped me save 3,200 KES on my laptop purchase. The price history feature showed me exactly when to buy.",
      name: "Faith Wanjiku",
      product: "HP Laptop",
      savings: "3,200 KES"
    },
    {
      quote: "I was about to buy a TV at full price, but Thamani alerted me to a flash sale the next day. Ended up saving 12,000 KES! Absolutely recommend.",
      name: "Michael Omondi",
      product: "LG Smart TV",
      savings: "12,000 KES"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 }
    }
  };

  return (
    <section id="testimonials" className="py-20" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">What Our Users Say</h2>
          <div className="w-20 h-1 bg-primary mx-auto mb-6"></div>
          <p className="text-lg font-serif text-muted-foreground max-w-3xl mx-auto">
            Join thousands of Kenyans who are saving money on their online purchases
          </p>
        </div>

        <motion.div 
          className="grid md:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          {testimonials.map((testimonial, index) => (
            <motion.div 
              key={index} 
              className="bg-secondary p-8 border border-border relative"
              variants={itemVariants}
            >
              <div className="absolute top-6 right-6 text-primary opacity-20">
                <Quote size={40} />
              </div>
              <p className="font-serif mb-6 relative z-10">{testimonial.quote}</p>
              <div className="mt-auto">
                <p className="font-serif font-bold">{testimonial.name}</p>
                <p className="text-sm text-muted-foreground">Saved <span className="font-bold text-success">{testimonial.savings}</span> on {testimonial.product}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default Testimonials;
