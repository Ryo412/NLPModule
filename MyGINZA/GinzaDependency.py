import spacy
import ginza

class Arcs:
    """
    係り受け元、係り受け先の位置と種類を記録する。

    Attributes
    ----------
    start : int
        係り受け元の位置
    end : int
        係り受け先の位置
    label : string
        係り受けの種類
    """

    def __init__(self,arcs):
        """
        Parameters
        ----------
        arcs : dict
            係り受けの位置と種類
        """
        self.start = arcs['start']
        self.end = arcs['end']
        self.label = arcs['label']

    def __repr__(self):
        return self.label

class WordFeature:
    """
    主辞単語、もしくは文節を保持する。

    Attributes
    ----------
    word : spacy.tokens.span.Span
        文節もしくは主辞単語
    number : int
        その文章における文節番号
    tokens : list
        文節もしくは主辞単語を構成する単語のリスト
    left_words : list
        左側にかかる係り受けのリスト
    right_words : list
        右側にかかる係り受けのリスト
    
    """
    def __init__(self, word:spacy.tokens.span.Span, number:int, tokens):
        """
        Parameters
        ----------
        word : spacy.tokens.span.Span
            文節もしくは主辞単語
        number : int
            その文章における文節番号
        tokens : list
            文節もしくは主辞単語を構成する単語のリスト
        """
        self.word = word
        self.number = number
        self.tokens = tokens
        self.left_words = []
        self.right_words = []

    def __repr__(self):
        return self.word.text

    def append_arcs(self, arcs, direction):
        """
        係り受け関係を追加する

        Parameters
        ----------
        arcs : dict
            係り受けの位置と種類
        direction : string
            係り受けの向き　(leftかright)
        """
        if(direction=="left"):
            self.left_words.append(Arcs(arcs))
        elif(direction=="right"):
            self.right_words.append(Arcs(arcs))
        else:
            print('Different format in arcs input.')

class SentenceFeature:
    """
    文章を保持する。
        
    Attributes
    ----------
    sentence : string
        該当の文章
    word_list : list
        含まれる文節か主辞単語のリスト
    number : int
        文書における文章番号
    """
    
    def __init__(self, sentence, word_list, number):
        """
        Parameters
        ----------
        sentence : string
            該当の文章
        word_list : list
            含まれる文節か主辞単語のリスト
        number : int
            文書における文章番号
        """
        self.sentence = sentence
        self.word_list = word_list
        self.number = number
        self.max_count = len(word_list)
        self.current = 0

    def __repr__(self):
        return self.sentence


    def search_start_word_end_word(self, word):
        """
        入力した単語と係り受け関係にある単語を出力する。

        Parameters
        ----------
        word : spacy.tokens.span.Span
            文節もしくは主辞単語

        Returns
        -------
        dict
            左側にかかる単語のリストと右側にかかる単語のリスト
        """
        if (word not in self.word_list):
            print('The input word is not included this sentence')
            return
        left_words = []
        right_words = []

        # 左側にかかる単語を記録
        for left_word in word.left_words:
            for word_ in self.word_list:
                if(left_word.start == word_.number):
                    left_words.append([word_, left_word.label])

        # 右側にかかる単語を記録
        for right_word in word.right_words:
            for word_ in self.word_list:
                if(right_word.start == word_.number):
                    right_words.append([word_, left_word.label])
    
        return {'left':left_words, 'right':right_words}

class DependencyAnalysis:
    """
    ginzaを用いた形態素解析を行う。

    Attributes
    ----------
    nlp : spacy.lang.ja.Japanese
        ja_ginza か ja_ginza_electra
    document : string
        分析対象のテキスト
    
    """
    def __init__(self, use_electra:bool=True):
        """
        Parameters:
        --------
        use_electra : bool
          electra modelを用いるか
        """
        self.nlp = spacy.load("ja_ginza_electra" if use_electra else "ja_ginza")
        self.model = "ja_ginza_electra"if use_electra else "ja_ginza"
        self.document = None

    def __repr__(self):
        return self.model
    
    def read_text(self,text):
        '''
        テキストの読み込み

        Parameters:
        --------
        text : str
            分析対象のテキスト
        '''
        self.document = text

    def analysis(self,text:str=None):
        """
        ginzaを用いて形態素解析

        Parameters
        ----------
        text : str
            分析対象のテキスト, by default None

        Returns
        -------
        doc
            形態素解析の結果
        """
        return self.nlp(self.document if text == None else text)
    
    def to_dependency_data(self, text:str=None, WorP:bool=True):
        """
        文節ごとの係り受けを表現

        Parameters
        ----------
        text : string
            分析対象のテキスト
        WorP : bool
            単語で出力するか、文節で出力するかを選択。\n
            Trueで主辞単語、Falseで文節


        Returns
        -------
        document : list
            文章区切りになったテキストの分析結果
        """
        doc = self.nlp(self.document if text == None else text) # 入力があればそれを使用なければdocument
        document = []
        for sent_number, sent in enumerate(doc.sents):
            words = []  #単語のlist
            bunsetu_head_list = ginza.bunsetu_head_list(doc)    #各文節の主辞となるtokenの位置を保存
            func = ginza.bunsetu_phrase_spans if WorP else ginza.bunsetu_spans #主辞単語の係り受けか、文節の係り受けか選択

            for chunk_number, chunk in enumerate(func(sent)):
                arcs_left = []      #左にかかる係り受け
                arcs_right = []     #右にかかる係り受け
                
                # 単語をWordFeatureクラスに変換
                word = WordFeature(chunk, chunk_number ,[token for token in chunk])

                #左側からの係り受け関係
                for token in chunk.lefts:
                    try:
                        arcs_left.append({
                            'start': bunsetu_head_list.index(token.i),  # 係り受け元
                            'end': chunk_number,                        # 自分
                            'label': token.dep_,                        # 係り受けの種類
                        })
                    except  ValueError: #もし指定tokenの位置に主辞tokenがない場合、スキップする。
                        continue
                #右への係り受け関係
                for token in chunk.rights:
                    try:
                        arcs_right.append({
                            'start': chunk_number,                      # 自分
                            'end': bunsetu_head_list.index(token.i),    # 係り受け先 
                            'label': token.dep_,                        # 係り受けの種類
                        })
                    except ValueError:  #もし指定tokenの位置に主辞tokenがない場合、スキップする。
                        continue

                for arcs in arcs_left: word.append_arcs(arcs, 'left')   # 左からの係り受けを追加
                for arcs in arcs_right: word.append_arcs(arcs, 'right') # 右への係り受けを追加
                words.append(word)
            document.append(SentenceFeature(sent.text,words, sent_number))
        return document
