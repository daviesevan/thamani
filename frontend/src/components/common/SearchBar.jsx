import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

const SearchBar = ({ placeholder = 'Search...', onSearch, className = '' }) => {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  const clearSearch = () => {
    setQuery('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`relative ${className}`}>
      <div className={`flex items-center border ${isFocused ? 'border-primary' : 'border-border'} bg-background transition-colors`}>
        <span className="pl-3 text-muted-foreground">
          <Search size={18} />
        </span>
        <input
          type="text"
          placeholder={placeholder}
          className="w-full py-2 px-3 bg-transparent focus:outline-none font-serif text-sm"
          value={query}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
        {query && (
          <button
            type="button"
            onClick={clearSearch}
            className="pr-3 text-muted-foreground hover:text-foreground"
          >
            <X size={18} />
          </button>
        )}
      </div>
    </form>
  );
};

export default SearchBar;
