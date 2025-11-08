'use client';

import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  className,
}: PaginationProps) {
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(startPage + maxVisiblePages - 1, totalPages);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  const pages = getPageNumbers();
  const showEllipsisStart = pages[0] > 1;
  const showEllipsisEnd = pages[pages.length - 1] < totalPages;

  if (totalPages <= 1) return null;

  return (
    <div className={cn('flex items-center justify-between', className)}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="gap-1.5"
      >
        <ChevronLeft className="h-4 w-4" />
        <span>Previous</span>
      </Button>

      <div className="hidden items-center gap-1 sm:flex">
        {showEllipsisStart && (
          <>
            <Button
              variant={currentPage === 1 ? 'default' : 'outline'}
              size="sm"
              className="h-9 w-9 p-0"
              onClick={() => onPageChange(1)}
            >
              1
            </Button>
            <Button variant="ghost" size="sm" className="h-9 w-9 p-0" disabled>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </>
        )}

        {pages.map((page) => (
          <Button
            key={page}
            variant={page === currentPage ? 'default' : 'outline'}
            size="sm"
            className="h-9 w-9 p-0"
            onClick={() => onPageChange(page)}
          >
            {page}
          </Button>
        ))}

        {showEllipsisEnd && (
          <>
            <Button variant="ghost" size="sm" className="h-9 w-9 p-0" disabled>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
            <Button
              variant={currentPage === totalPages ? 'default' : 'outline'}
              size="sm"
              className="h-9 w-9 p-0"
              onClick={() => onPageChange(totalPages)}
            >
              {totalPages}
            </Button>
          </>
        )}
      </div>

      <div className="flex items-center sm:hidden">
        <span className="text-sm font-medium">
          Page {currentPage} of {totalPages}
        </span>
      </div>

      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="gap-1.5"
      >
        <span>Next</span>
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}
