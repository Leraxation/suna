'use client';

import React from 'react';
import { Button } from '@/components/ui/button';

import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Paintbrush } from 'lucide-react';

export function StylePicker({ onStyleChange }: { onStyleChange: (emoji: string, color: string) => void }) {
  const emojis = ['🤖', '🦾', '🔮', '🌟', '⚡'];
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#D4A5A5'];

  const handleSelect = (index: number) => {
    onStyleChange(emojis[index], colors[index]);
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          <Paintbrush className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="grid grid-cols-5 gap-2">
          {emojis.map((emoji, index) => (
            <Button
              key={index}
              variant="outline"
              className="h-10 w-10"
              style={{ backgroundColor: colors[index] }}
              onClick={() => handleSelect(index)}
            >
              {emoji}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}