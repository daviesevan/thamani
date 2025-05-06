import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { BellRing, LineChart, BarChart3, Award } from 'lucide-react';

const KeyFeatures = () => {
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, amount: 0.3 });

  const features = [
    {
      icon: <BellRing size={32} />,
      title: "Price Drop Alerts",
      description: "Get notified instantly when prices fall below your target"
    },
    {
      icon: <LineChart size={32} />,
      title: "Price History Charts",
      description: "See how prices have changed over time to make informed decisions"
    },
    {
      icon: <BarChart3 size={32} />,
      title: "Multiple Retailer Comparison",
      description: "Compare prices across Kenya's top online shops"
    },
    {
      icon: <Award size={32} />,
      title: "Deal Rating System",
      description: "Our algorithm tells you how good a current price is compared to historical data"
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
    <section id="features" className="py-20 bg-secondary" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">Key Features</h2>
          <div className="w-20 h-1 bg-primary mx-auto mb-6"></div>
          <p className="text-lg font-serif text-muted-foreground max-w-3xl mx-auto">
            Tools designed to help you make smarter shopping decisions
          </p>
        </div>

        <motion.div 
          className="grid md:grid-cols-2 gap-12"
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          {features.map((feature, index) => (
            <motion.div 
              key={index} 
              className="flex items-start"
              variants={itemVariants}
            >
              <div className="flex-shrink-0 mr-6 text-primary">
                {feature.icon}
              </div>
              <div>
                <h3 className="text-xl font-serif font-bold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground font-serif">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default KeyFeatures;
