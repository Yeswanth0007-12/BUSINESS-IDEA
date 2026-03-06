import { ReactNode, useState } from 'react';

interface Column<T> {
  key: string;
  label: string;
  render?: (item: T) => ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  emptyMessage?: string;
}

function DataTable<T extends { id: number | string }>({
  columns,
  data,
  onEdit,
  onDelete,
  emptyMessage = 'No data available',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('asc');
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortKey) return 0;

    const aValue = (a as any)[sortKey];
    const bValue = (b as any)[sortKey];

    if (aValue === bValue) return 0;

    const comparison = aValue > bValue ? 1 : -1;
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  if (data.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg p-12 border border-slate-700 text-center">
        <p className="text-slate-400 text-lg">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider ${
                    column.sortable ? 'cursor-pointer hover:bg-slate-600' : ''
                  }`}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center">
                    {column.label}
                    {column.sortable && sortKey === column.key && (
                      <svg
                        className={`w-4 h-4 ml-1 transition-transform ${
                          sortOrder === 'desc' ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 15l7-7 7 7"
                        />
                      </svg>
                    )}
                  </div>
                </th>
              ))}
              {(onEdit || onDelete) && (
                <th className="px-6 py-3 text-right text-xs font-medium text-slate-300 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {sortedData.map((item) => (
              <tr key={item.id} className="hover:bg-slate-700/50 transition">
                {columns.map((column) => (
                  <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    {column.render ? column.render(item) : String((item as any)[column.key])}
                  </td>
                ))}
                {(onEdit || onDelete) && (
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(item)}
                        className="text-blue-400 hover:text-blue-300 mr-4 transition"
                      >
                        Edit
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={() => onDelete(item)}
                        className="text-red-400 hover:text-red-300 transition"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
