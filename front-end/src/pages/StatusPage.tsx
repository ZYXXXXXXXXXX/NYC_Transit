import React, { useEffect, useState } from 'react';
import { Box, Button, Checkbox, FormControlLabel, FormGroup, Typography, CircularProgress } from '@mui/material';
import initSqlJs, { Database } from 'sql.js';

const subwayLines = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'J', 'L', 'M', 'N', 'Q', 'R', 'W', 'Z'];

export default function StatusPage() {
  const [db, setDb] = useState<Database | null>(null);
  const [selectedLines, setSelectedLines] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDb = async () => {
      const SQL = await initSqlJs({
        locateFile: (file) => `https://sql.js.org/dist/${file}`,
      });
      const database = new SQL.Database();

      // 创建表
      database.run(`
        CREATE TABLE IF NOT EXISTS favorite_lines (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          line TEXT
        );
      `);

      // 加载之前保存的选项
      const result = database.exec('SELECT line FROM favorite_lines;');
      if (result.length > 0) {
        const lines = result[0].values.map((row) => row[0] as string);
        setSelectedLines(lines);
      }

      setDb(database);
      setLoading(false);
    };

    loadDb();
  }, []);

  const handleToggle = (line: string) => {
    setSelectedLines((prev) =>
      prev.includes(line) ? prev.filter((l) => l !== line) : [...prev, line]
    );
  };

  const saveFavoriteLines = () => {
    if (!db) return;

    // 先清空
    db.run('DELETE FROM favorite_lines;');

    // 再插入
    selectedLines.forEach((line) => {
      db.run('INSERT INTO favorite_lines (line) VALUES (?);', [line]);
    });

    alert('Saved successfully to SQLite!');
  };

  const clearFavoriteLines = () => {
    if (!db) return;

    db.run('DELETE FROM favorite_lines;');
    setSelectedLines([]);
    alert('Cleared all favorite lines.');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box marginTop="80px" padding={2}>
      <Typography variant="h4" gutterBottom>
        Select Your Favorite Subway Lines
      </Typography>

      <FormGroup>
        {subwayLines.map((line) => (
          <FormControlLabel
            key={line}
            control={
              <Checkbox
                checked={selectedLines.includes(line)}
                onChange={() => handleToggle(line)}
              />
            }
            label={`Line ${line}`}
          />
        ))}
      </FormGroup>

      <Box mt={3} display="flex" gap={2}>
        <Button variant="contained" color="primary" onClick={saveFavoriteLines}>
          Save
        </Button>
        <Button variant="outlined" color="secondary" onClick={clearFavoriteLines}>
          Clear
        </Button>
      </Box>
    </Box>
  );
}