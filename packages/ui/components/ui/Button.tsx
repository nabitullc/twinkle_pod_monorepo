import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = ({ 
  variant = 'primary', 
  size = 'md',
  className = '', 
  children, 
  ...props 
}: ButtonProps) => {
  const baseStyles = 'font-semibold rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-purple-600 text-white hover:bg-purple-700 shadow-sm hover:shadow-md active:scale-95',
    secondary: 'bg-amber-500 text-white hover:bg-amber-600 shadow-sm hover:shadow-md active:scale-95',
    outline: 'border-2 border-purple-600 text-purple-600 hover:bg-purple-50 active:scale-95',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`} 
      {...props}
    >
      {children}
    </button>
  );
};
