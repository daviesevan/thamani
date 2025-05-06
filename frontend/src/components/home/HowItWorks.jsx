import React, { useRef } from 'react';
import { Link, Bell, TrendingDown } from 'lucide-react';
import { motion, useInView } from 'framer-motion';

const HowItWorks = () => {
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.3 });

  const steps = [
    {
      icon: <Link size={32} />,
      title: "Add Products",
      description: "Add products you're interested in by pasting links or searching"
    },
    {
      icon: <Bell size={32} />,
      title: "Set Target Price",
      description: "Set your target price and get notified when prices drop"
    },
    {
      icon: <TrendingDown size={32} />,
      title: "Save Money",
      description: "Save money by buying at the right time"
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
    <section id="how-it-works" className="py-20 bg-secondary" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">How It Works</h2>
          <div className="w-20 h-1 bg-primary mx-auto"></div>
        </div>

        <motion.div 
          className="grid md:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          {steps.map((step, index) => (
            <motion.div 
              key={index} 
              className="flex flex-col items-center text-center p-6"
              variants={itemVariants}
            >
              <div className="w-16 h-16 flex items-center justify-center mb-6 text-primary">
                {step.icon}
              </div>
              <h3 className="text-xl font-serif font-bold mb-3">{step.title}</h3>
              <p className="text-muted-foreground font-serif">{step.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;
