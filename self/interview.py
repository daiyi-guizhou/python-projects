"""


"""

class Solution(object):
    def subarraysEqualK(self, _index):
        """
        :type _index: int
        """
        if _index == len(self.a): return
        self._sum.append(self.a[_index])
        if self._sum:
            if sum(self._sum) == self.k: 
                self._res.append([_ for _  in self._sum])
            else:
                if abs(sum(self._sum) - self.k) < self.minus:
                    self.minus = abs(sum(self._sum) - self.k)
                    self.minus_list = [_ for _ in self._sum]
        self.subarraysEqualK(_index +1)
        self._sum.pop()         
        self.subarraysEqualK(_index +1)

    def main(self, A, K):
        """
        :type A: List[int]
        :type K: int
        :rtype: List
        """
        if not A or not K: return
        self.k, self.a, self.minus = K, A, K
        self._sum, self._res, self.minus_list = [], [], []
        self.subarraysEqualK(0)
        print self._res if self._res else self.minus_list


a = Solution()
a.main([1,2,3,4,5,6], 6)
a.main([1,2,3,4,5], 100)