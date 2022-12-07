import mojimoji
import re

class PreCleaningText:
    """
    テキストの前処理を行う
    """
    def run_all_method(self, text):
        """
        全てのメソッドを呼び出す。
        """
        cleaned_text = text
        cleaned_text = self.delete_parentheses(cleaned_text)
        cleaned_text = self.replace_punctuation(cleaned_text)
        cleaned_text = self.double_char_to_single_char(cleaned_text)
        cleaned_text = self.single_char_to_double_char(cleaned_text)
        cleaned_text = self.alphabet_to_lower(cleaned_text)
        cleaned_text = self.normalize_number(cleaned_text)
        
        return cleaned_text

    def delete_parentheses(self, text):
        """
        括弧を削除し空白で置換する。

        Parameters
        ----------
        text : string
            対象となるテキスト
        """
        delete_target = "[\(\)<>\[\]\{\}（）＜＞［］｛｝｟｠｢｣〈〉《》「」『』【】〔〕〖〗〘〙〚〛⟦⟧⟨⟩⟪⟫⟬⟭⟮⟯⦃⦄⦅⦆⦇⦈⦉⦊⦋⦌⦍⦎⦏⦐⦑⦒⦗⦘⧼⧽❨❩❪❫❬❭❮❯❰❱❲❳❴❵⁽⁾₍₎]"        
        cleaned_text = re.sub(delete_target, ' ', text)
        return cleaned_text

    def replace_punctuation(self, text):
        """
        句読点(、。）を（､｡）に置き換える。

        Parameters
        ----------
        text : string
            対象となるテキスト
        """
        target_words = ['、', '。']
        replaced_words = [',', '.']
        cleaned_text = text

        for target, replaced in zip(target_words, replaced_words):
            cleaned_text = cleaned_text.replace(target, replaced)

        return cleaned_text

    def double_char_to_single_char(self,text):
        """
        全角文字(数字、アルファベット、)を半角に変更

        Parametersß
        ----------
        text : string
            対象となるテキスト
        """
        return mojimoji.zen_to_han(text,kana=False)

    def single_char_to_double_char(self, text, alphabet:bool=False):
        """
        半角文字（カタカナ）を全角に変更

        Parameters
        ----------
        text : string
            対象となるテキスト
        alphabet : bool, optional
            アルファベットを全角にする場合はTrue, by default False
        
        """
        return mojimoji.han_to_zen(text,ascii=False,digit=False)

    def alphabet_to_lower(self, text):
        """
        大文字のアルファベットを小文字に変換

        Parameters
        ----------
        text : string
            対象となるテキスト
        """
        return text.lower()
        
    def normalize_number(self, text, replace_number_char = '0'):
        """
        数字を任意の数に置き換え
        ※一般的に数値表現は自然言語のタスクにおいて利用されない場合が多い

        Parameters
        ----------
        replace_number : char, optional
            置き換える文字を指定, by default 0
        """
        cleaned_text = re.sub(r'\d+', replace_number_char, text)
        return cleaned_text






a = PreCleaningText()
text = '江頭2:50は40度の高熱が出たが、Ｆｉｎｅでギャラを『500円』ﾏｼでもらった。'
text_ = a.run_all_method(text)
print(text_)