#Author: Jared Adolf-Bryfogle

import sys
import logging
import pandas

from typing import List, Dict
from collections import defaultdict

from pic2.modules.restype_definitions import definitions


class SequenceStats:
    """
    Class for getting data from an array of sequences of equal length.
    """

    def __init__(self, sequence_list: List[str]):
        self.sequence_list = sequence_list
        if len(self.sequence_list)==0:
            print("No sequences found.")
            return

        self.prob: List[Dict[str, float]] = [] #Probability of each amino acid at each position
        self.freq:  List[Dict[str, int]]   = [] #Frequency of each amino acid at each position

        self.aas: List[str] = definitions().get_all_one_letter_codes()
        self._compute_stats()

    def set_sequences(self, sequence_list: List[str]):
        """
        Set a sequence list, compute stats
        """

        self.sequence_list = sequence_list
        self._compute_stats()

    def get_probability(self, position: int, aa: str) -> float:
        '''
        Get probability of the current position (starting from 0) and aa
        '''

        try:
            if aa not in self.prob[position]:
                return 0
        except IndexError:
            sys.exit("Position not found in stats.  This is bad. We have a problem")

        return self.prob[position][aa]

    def get_frequency(self, position: int, aa: str) -> int:
        return self.freq[position][aa]

    def get_dataframe(self) -> pandas.DataFrame:
        """
        Get all data as a dataframe
        """
        rows = []
        for position in range(0, len(self.prob)):
            for aa in self.prob[position]:
                dat = defaultdict()
                dat['position'] = position
                dat['aa'] = aa
                dat['frequency'] = self.get_frequency(position, aa)
                dat['probability'] = self.get_probability(position, aa)
                rows.append(dat)
        return pandas.DataFrame(rows)
    def get_consensus_sequence(self) -> str:
        """
        Get a computed consensus sequence.
        AA with prob x >.9       are CAPITALIZED
                prob .9 < x > .2 are lowercased
                prob x < .2      are '-'
        """
        consensus = ""
        for position in range(0, len(self.prob)):
            pos = position
            aa_letter = ""
            for aa in self.prob[pos]:
                prob = self.prob[pos][aa]
                if prob > .9:
                    aa_letter = aa.upper()
                    break
                elif prob > .2:
                    aa_letter = aa.lower()
                    break
                else:
                    aa_letter = '-'
                    continue

            consensus = consensus+aa_letter

        return consensus


    ########################
    def _compute_stats(self):
        """
        Sets all probabilities 0 and appends each map to the stats vector
        Compute frequency and probability (0-1) for each position for each amino acid
        """

        def _get_initialized_total_map() -> Dict[str, int]:
            local_totals = dict()
            for aa in self.aas:
                local_totals[aa] = 0

            return local_totals

        self.prob.clear()
        self.freq.clear()

        if len(self.sequence_list) == 0: return

        for i in range(1, len(self.sequence_list[0])+1):
            prob = dict()
            freq = dict()
            for aa in self.aas:
                prob[aa] = 0
                freq[aa] = 0
            self.prob.append(prob)
            self.freq.append(freq)

        logging.info("Total Sequences: "+repr(len(self.sequence_list)))

        #Check to make sure all lengths are even.
        length = len(self.sequence_list[0])
        for seq in self.sequence_list:
            if len(seq) != length:
                sys.exit("SequenceStats: Lengths must be even!!")

        for position in range(0, len(self.sequence_list[0])):

            totals = _get_initialized_total_map()
            for seq in self.sequence_list:

                totals[seq[position]]+=1
            for aa in totals:

                self.prob[position][aa] = totals[aa]/float(len(self.sequence_list))
                self.freq[position][aa] = totals[aa]




