class IntervalNode:
    """Node in the Interval Tree."""
    
    def __init__(self, interval):
        self.interval = interval  # (start, end)
        self.max_high = interval[1]
        self.left = None
        self.right = None
        self.height = 1


class IntervalTree:
    """Self-balancing Interval Tree for efficient overlap detection.
    
    Time Complexity:
    - Insert: O(log n)
    - Delete: O(log n)
    - Search (overlap): O(log n)
    
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self.root = None
    
    def insert(self, interval):
        """Insert an interval into the tree."""
        self.root = self._insert_recursive(self.root, interval)
    
    def _insert_recursive(self, node, interval):
        if node is None:
            return IntervalNode(interval)
        
        if interval[0] < node.interval[0]:
            node.left = self._insert_recursive(node.left, interval)
        else:
            node.right = self._insert_recursive(node.right, interval)
        
        node.max_high = max(node.max_high, interval[1])
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        return self._balance(node)
    
    def search_overlap(self, interval):
        """Find all intervals that overlap with the given interval.
        
        Returns list of overlapping intervals.
        """
        result = []
        self._search_overlap_recursive(self.root, interval, result)
        return result
    
    def _search_overlap_recursive(self, node, interval, result):
        if node is None:
            return
        
        # Check if current node's interval overlaps
        if self._intervals_overlap(node.interval, interval):
            result.append(node.interval)
        
        # If left subtree could have overlaps
        if node.left and node.left.max_high >= interval[0]:
            self._search_overlap_recursive(node.left, interval, result)
        
        # If right subtree could have overlaps
        if node.right and interval[1] >= node.interval[0]:
            self._search_overlap_recursive(node.right, interval, result)
    
    def delete(self, interval):
        """Delete an interval from the tree."""
        self.root = self._delete_recursive(self.root, interval)
    
    def _delete_recursive(self, node, interval):
        if node is None:
            return None
        
        if interval[0] < node.interval[0]:
            node.left = self._delete_recursive(node.left, interval)
        elif interval[0] > node.interval[0]:
            node.right = self._delete_recursive(node.right, interval)
        else:
            # Found the node to delete
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Find in-order successor
                min_node = self._find_min(node.right)
                node.interval = min_node.interval
                node.right = self._delete_recursive(node.right, min_node.interval)
        
        if node:
            node.max_high = max(node.interval[1], 
                               max(self._get_max_high(node.left), 
                                   self._get_max_high(node.right)))
            node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
            return self._balance(node)
        
        return node
    
    def _find_min(self, node):
        while node.left:
            node = node.left
        return node
    
    def _get_height(self, node):
        return node.height if node else 0
    
    def _get_max_high(self, node):
        return node.max_high if node else 0
    
    def _get_balance_factor(self, node):
        """Calculate balance factor for AVL balancing."""
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)
    
    def _rotate_right(self, node):
        """Right rotation for AVL balancing."""
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        
        # Update heights and max_high
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.max_high = max(node.interval[1], 
                           max(self._get_max_high(node.left), self._get_max_high(node.right)))
        left_child.height = 1 + max(self._get_height(left_child.left), self._get_height(left_child.right))
        left_child.max_high = max(left_child.interval[1],
                                  max(self._get_max_high(left_child.left), self._get_max_high(left_child.right)))
        
        return left_child
    
    def _rotate_left(self, node):
        """Left rotation for AVL balancing."""
        right_child = node.right
        node.right = right_child.left
        right_child.left = node
        
        # Update heights and max_high
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.max_high = max(node.interval[1],
                           max(self._get_max_high(node.left), self._get_max_high(node.right)))
        right_child.height = 1 + max(self._get_height(right_child.left), self._get_height(right_child.right))
        right_child.max_high = max(right_child.interval[1],
                                   max(self._get_max_high(right_child.left), self._get_max_high(right_child.right)))
        
        return right_child
    
    def _balance(self, node):
        """Perform AVL balancing on node."""
        balance = self._get_balance_factor(node)
        
        # Left heavy
        if balance > 1:
            if self._get_balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Right heavy
        if balance < -1:
            if self._get_balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    @staticmethod
    def _intervals_overlap(interval1, interval2):
        """Check if two intervals overlap."""
        return interval1[0] < interval2[1] and interval2[0] < interval1[1]
