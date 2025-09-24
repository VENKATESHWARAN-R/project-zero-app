/**
 * Footer component
 * Site footer with links, information, and newsletter signup
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Package,
  Mail,
  Phone,
  MapPin,
  Facebook,
  Twitter,
  Instagram,
  Github,
  ArrowRight
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useToast } from '@/components/ui/Toast';
import { cn } from '@/lib/utils';
import { ROUTES, APP_CONFIG } from '@/lib/constants';

interface FooterLinkSection {
  title: string;
  links: Array<{
    label: string;
    href: string;
    external?: boolean;
  }>;
}

const footerSections: FooterLinkSection[] = [
  {
    title: 'Shop',
    links: [
      { label: 'All Products', href: ROUTES.PRODUCTS },
      { label: 'Electronics', href: '/categories/electronics' },
      { label: 'Clothing', href: '/categories/clothing' },
      { label: 'Home & Garden', href: '/categories/home' },
      { label: 'Sports', href: '/categories/sports' },
    ],
  },
  {
    title: 'Account',
    links: [
      { label: 'My Profile', href: ROUTES.PROFILE },
      { label: 'Order History', href: '/orders' },
      { label: 'Wishlist', href: '/wishlist' },
      { label: 'Account Settings', href: '/settings' },
    ],
  },
  {
    title: 'Support',
    links: [
      { label: 'Help Center', href: '/help' },
      { label: 'Contact Us', href: '/contact' },
      { label: 'Shipping Info', href: '/shipping' },
      { label: 'Returns', href: '/returns' },
      { label: 'Size Guide', href: '/size-guide' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About Us', href: '/about' },
      { label: 'Careers', href: '/careers' },
      { label: 'Press', href: '/press' },
      { label: 'Blog', href: '/blog' },
      { label: 'Affiliate Program', href: '/affiliate' },
    ],
  },
];

const socialLinks = [
  {
    name: 'Facebook',
    href: 'https://facebook.com',
    icon: Facebook,
    color: 'hover:text-blue-600'
  },
  {
    name: 'Twitter',
    href: 'https://twitter.com',
    icon: Twitter,
    color: 'hover:text-blue-400'
  },
  {
    name: 'Instagram',
    href: 'https://instagram.com',
    icon: Instagram,
    color: 'hover:text-pink-600'
  },
  {
    name: 'GitHub',
    href: 'https://github.com',
    icon: Github,
    color: 'hover:text-gray-900'
  },
];

export function Footer() {
  const [email, setEmail] = useState('');
  const [isSubscribing, setIsSubscribing] = useState(false);
  const { success, error } = useToast();

  const handleNewsletterSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      error('Please enter a valid email address');
      return;
    }

    setIsSubscribing(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      success('Thank you for subscribing to our newsletter!');
      setEmail('');
    } catch (err) {
      error('Failed to subscribe. Please try again.');
    } finally {
      setIsSubscribing(false);
    }
  };

  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white">
      {/* Newsletter Section */}
      <div className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold mb-4">
              Stay Updated
            </h3>
            <p className="text-gray-400 mb-6">
              Subscribe to our newsletter for the latest products, exclusive deals, and updates.
            </p>

            <form onSubmit={handleNewsletterSubscribe} className="flex max-w-md mx-auto">
              <Input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-r-none border-gray-600 bg-gray-800 text-white placeholder-gray-400"
                required
              />
              <Button
                type="submit"
                loading={isSubscribing}
                className="rounded-l-none"
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Subscribe
              </Button>
            </form>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Brand and Description */}
          <div className="lg:col-span-2">
            <Link href={ROUTES.HOME} className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">{APP_CONFIG.name}</span>
            </Link>

            <p className="text-gray-400 mb-6 max-w-md">
              {APP_CONFIG.description}. Discover amazing products with fast shipping and excellent customer service.
            </p>

            {/* Contact Info */}
            <div className="space-y-3 text-sm text-gray-400">
              <div className="flex items-center space-x-3">
                <Mail className="w-4 h-4 flex-shrink-0" />
                <span>{APP_CONFIG.email}</span>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="w-4 h-4 flex-shrink-0" />
                <span>1-800-PROJECT-ZERO</span>
              </div>
              <div className="flex items-center space-x-3">
                <MapPin className="w-4 h-4 flex-shrink-0" />
                <span>123 Commerce Street, Tech City, TC 12345</span>
              </div>
            </div>
          </div>

          {/* Footer Link Sections */}
          {footerSections.map((section) => (
            <div key={section.title}>
              <h4 className="text-lg font-semibold mb-4">{section.title}</h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.href}>
                    {link.external ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-white transition-colors text-sm"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <Link
                        href={link.href}
                        className="text-gray-400 hover:text-white transition-colors text-sm"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Footer */}
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            {/* Copyright */}
            <div className="text-sm text-gray-400 mb-4 md:mb-0">
              <p>
                © {currentYear} {APP_CONFIG.name}. All rights reserved.
              </p>
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-4 mb-4 md:mb-0">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={cn(
                      'text-gray-400 transition-colors',
                      social.color
                    )}
                    aria-label={`Follow us on ${social.name}`}
                  >
                    <Icon className="w-5 h-5" />
                  </a>
                );
              })}
            </div>

            {/* Legal Links */}
            <div className="flex items-center space-x-6 text-sm">
              <Link
                href="/privacy"
                className="text-gray-400 hover:text-white transition-colors"
              >
                Privacy Policy
              </Link>
              <Link
                href="/terms"
                className="text-gray-400 hover:text-white transition-colors"
              >
                Terms of Service
              </Link>
              <Link
                href="/cookies"
                className="text-gray-400 hover:text-white transition-colors"
              >
                Cookie Policy
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Trusted Badges Section */}
      <div className="bg-gray-800 border-t border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-8">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
              <span>Secure Payment</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">🚚</span>
              </div>
              <span>Free Shipping Over $50</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">↩</span>
              </div>
              <span>30-Day Returns</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <div className="w-6 h-6 bg-orange-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">24/7</span>
              </div>
              <span>Customer Support</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;