import jieba

class CommentJudge():
    def getBest(self, comments):
        self.comments = comments
        self.segment_comments = []
        self.wordDict = {}
        self.commentsScore = []

        self.segment()
        self.buildWordDict()
        self.score()

        maxScore, maxIndex = 0, 0
        for index in range(len(self.commentsScore)):
            score = self.commentsScore[index]
            if score > maxScore:
                maxScore = score
                maxIndex = index
        return self.comments[maxIndex], self.commentsScore[maxIndex]
    
    def segment(self):
        banned = [' ', ',', '，', '。', '？', '?', '=']
        for comment in self.comments:
            words = [ word for word in jieba.cut(comment) if word not in banned]
            self.segment_comments.append(words)

    def buildWordDict(self):
        for comment in self.segment_comments:
            for word in comment:
                if word in self.wordDict:
                    self.wordDict[word] += 1
                else:
                    self.wordDict[word] = 0
        # print(self.wordDict)
    
    def score(self):
        for index in range(len(self.segment_comments)):
            comment = self.segment_comments[index]
            if len(self.comments[index]) >= 15:
                self.commentsScore.append(0)
                continue

            weight = 0
            for word in comment:
                weight += self.wordDict[word]

            self.commentsScore.append(weight)
