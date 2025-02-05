
## 4. Export and Backup

### 4.1 Dataset Export
**Actor**: Contributor

**Flow**:
1. Selects export format (JSONL)
2. Chooses export options:
   - Include all images
   - Only reviewed captions
   - Selected subset
3. Specifies export location
4. Generates export package
5. Reviews export summary

**Success Criteria**:
- Correct JSONL formatting
- Complete metadata
- Export verification

### 4.2 Work Session Management
**Actor**: Contributor

**Flow**:
1. Saves current work session
2. Includes:
   - Loaded images
   - Generated captions
   - Review status
   - Custom settings
3. Loads previous sessions
4. Merges sessions if needed

**Success Criteria**:
- Reliable session storage
- Easy session recovery
- Session merge support