import React, { useState } from 'react';
import Loader, { ButtonLoader, FullPageLoader, SkeletonLoader } from '../components/common/Loader';
import CustomButton from '../components/common/CustomButton';

const LoaderDemo = () => {
  const [showFullPageLoader, setShowFullPageLoader] = useState(false);

  const toggleFullPageLoader = () => {
    setShowFullPageLoader(true);
    // Automatically hide after 3 seconds
    setTimeout(() => {
      setShowFullPageLoader(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-serif font-bold">Thamani</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-serif font-bold mb-8">Loader Components</h1>

        {/* Dots Loader Section */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Dots Loader</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 p-6 border border-border">
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Small</h3>
              <Loader variant="dots" size="sm" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Medium</h3>
              <Loader variant="dots" size="md" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Large</h3>
              <Loader variant="dots" size="lg" />
            </div>
          </div>
        </section>

        {/* Spinner Loader Section */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Spinner Loader</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 p-6 border border-border">
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Small</h3>
              <Loader variant="spinner" size="sm" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Medium</h3>
              <Loader variant="spinner" size="md" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Large</h3>
              <Loader variant="spinner" size="lg" />
            </div>
          </div>
        </section>

        {/* Pulse Loader Section */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Pulse Loader</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 p-6 border border-border">
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Small</h3>
              <Loader variant="pulse" size="sm" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Medium</h3>
              <Loader variant="pulse" size="md" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Large</h3>
              <Loader variant="pulse" size="lg" />
            </div>
          </div>
        </section>

        {/* Bar Loader Section */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Bar Loader</h2>
          <div className="grid grid-cols-1 gap-8 p-6 border border-border">
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Small</h3>
              <Loader variant="bar" size="sm" className="w-full max-w-md" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Medium</h3>
              <Loader variant="bar" size="md" className="w-full max-w-md" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Large</h3>
              <Loader variant="bar" size="lg" className="w-full max-w-md" />
            </div>
          </div>
        </section>

        {/* Skeleton Loader Section */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Skeleton Loader</h2>
          <div className="p-6 border border-border">
            <SkeletonLoader className="max-w-md mx-auto" />
          </div>
        </section>

        {/* Loader with Text */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Loader with Text</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 p-6 border border-border">
            <div className="flex flex-col items-center">
              <Loader variant="dots" size="md" text="Loading..." />
            </div>
            <div className="flex flex-col items-center">
              <Loader variant="spinner" size="md" text="Please wait..." />
            </div>
            <div className="flex flex-col items-center">
              <Loader variant="pulse" size="md" text="Processing..." />
            </div>
          </div>
        </section>

        {/* Button Loader */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Button Loader</h2>
          <div className="p-6 border border-border">
            <div className="flex flex-wrap gap-4">
              <button className="px-4 py-2 bg-primary text-white dark:text-black font-serif flex items-center">
                <ButtonLoader />
                Loading
              </button>
              
              <button className="px-4 py-2 border border-border font-serif flex items-center">
                <ButtonLoader color="secondary" />
                Processing
              </button>
            </div>
          </div>
        </section>

        {/* Full Page Loader */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Full Page Loader</h2>
          <div className="p-6 border border-border">
            <CustomButton onClick={toggleFullPageLoader}>
              Show Full Page Loader (3 seconds)
            </CustomButton>
          </div>
        </section>

        {/* Different Colors */}
        <section className="mb-12">
          <h2 className="text-xl font-serif font-bold mb-4">Different Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 p-6 border border-border">
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Primary</h3>
              <Loader variant="dots" size="md" color="primary" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Secondary</h3>
              <Loader variant="dots" size="md" color="secondary" />
            </div>
            <div className="flex flex-col items-center">
              <h3 className="text-sm font-serif mb-4">Muted</h3>
              <Loader variant="dots" size="md" color="muted" />
            </div>
          </div>
        </section>
      </div>

      {showFullPageLoader && <FullPageLoader text="Loading, please wait..." />}
    </div>
  );
};

export default LoaderDemo;
