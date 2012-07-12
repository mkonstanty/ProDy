# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2012 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module defines classes for handling polypeptide/nucleic acid chains."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

import numpy as np

from subset import AtomSubset

__all__ = ['Chain']

AAMAP = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q', 
    'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 
    'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W', 
    'TYR': 'Y', 'VAL': 'V',
    'ASX': 'B', 'GLX': 'Z', 'SEC': 'U', 'PYL': 'O', 'XLE': 'J',
}
_ = {}
for aaa, a in AAMAP.iteritems():
    _[a] = aaa
AAMAP.update(_)
AAMAP.update({'PTR': 'Y', 'TPO': 'T', 'SEP': 'S', 'CSO': 'C',
              'HSD': 'H', 'HSP': 'H', 'HSE': 'H',})

def getSequence(resnames):
    """Return polypeptide sequence as from list of *resnames* (residue 
    name abbreviations)."""
    
    get = AAMAP.get
    return ''.join([get(rn, 'X') for rn in resnames])

class Chain(AtomSubset):
    
    """Instances of this class point to atoms with same chain identifiers and 
    are generated by :class:`~.HierView` class.  Following built-in functions
    are customized for this class:
    
    * :func:`len` returns the number of residues in the chain
    * :func:`iter` yields :class:`~.Residue` instances
    
    Indexing :class:`Chain` instances by:

         - *residue number [, insertion code]* (:func:`tuple`), 
           e.g. ``10`` or  ``10, "B"``, returns a :class:`~.Residue`
         - *slice* (:func:`slice`), e.g, ``10:20``, returns a list of  
           :class:`~.Residue` instances
    
    >>> from prody import *
    >>> pdb = parsePDB('1p38')
    >>> hv = pdb.getHierView()
    >>> chA = hv['A']
    >>> chA[4]
    <Residue: GLU 4 from Chain A from 1p38 (9 atoms)>
    >>> print chA[3] # Residue 3 does not exist in chain A
    None
    
    Iterating over a chain yields residue instances:
        
    >>> for res in chA: print res
    GLU 4
    ARG 5
    PRO 6
    THR 7
    ..."""
        
    def __init__(self, ag, indices, acsi=None, **kwargs):
        
        AtomSubset.__init__(self, ag, indices, acsi, **kwargs)
        
        self._seq = None
        self._dict = dict()
        self._list = list()
        
        segment = kwargs.get('segment')
        if segment is not None:
            segment._dict[self.getChid()] = len(segment._list)
            segment._list.append(self)
        self._segment = segment
        
    def __len__(self):
        
        return len(self._list)
    
    def __repr__(self):

        n_csets = self._ag.numCoordsets()
        segment = self._segment
        if segment is None:
            segment = ''
        else:
            segment = ' from ' + str(segment)
        if n_csets == 1:
            return ('<Chain: {0:s}{1:s} from {2:s} ({3:d} residues, {4:d} '
                    'atoms)>').format(self.getChid(), segment, 
                    self._ag.getTitle(), self.numResidues(), self.numAtoms())
        elif n_csets > 1:
            return ('<Chain: {0:s}{1:s} from {2:s} ({3:d} residues, {4:d} '
                    'atoms; active #{5:d} of {6:d} coordsets)>').format(
                    self.getChid(), segment, self._ag.getTitle(), 
                    self.numResidues(), self.numAtoms(), self.getACSIndex(), 
                    n_csets)
        else:
            return ('<Chain: {0:s}{1:s} from {2:s} ({3:d} residues, '
                    '{4:d} atoms; no coordinates)>').format(self.getChid(), 
                    segment, self._ag.getTitle(), self.numResidues(), 
                    self.numAtoms())

    def __str__(self):
        
        return 'Chain ' + self.getChid()
    
    def __getitem__(self, key):
        
        if isinstance(key, tuple): 
            return self.getResidue(*key) 
    
        elif isinstance(key, slice):
            resnums = self._getResnums()
            resnums = set(np.arange(*key.indices(resnums.max()+1)))
            _list = self._list
            return [_list[i] for (rn, ic), i in self._dict.iteritems() 
                    if rn in resnums]
                    
        else:
            return self.getResidue(key)
    
    def getSegment(self):
        """Return segment that this chain belongs to."""
        
        return self._segment
    
    def getSegname(self):
        """Return name of the segment that this chain belongs to."""
        
        if self._segment:
            return self._segment.getSegname()
    
    def getResidue(self, resnum, icode=None):
        """Return residue with number *resnum* and insertion code *icode*."""
        
        index = self._dict.get((resnum, icode or None))
        if index is not None:
            return self._list[index]

    def iterResidues(self):
        """Iterate residues in the chain."""
        
        return self._list.__iter__()
    
    __iter__ = iterResidues
    
    def numResidues(self):
        """Return number of residues."""
        
        return len(self._list)

    def getChid(self):
        """Return chain identifier."""
        
        return self._ag._getChids()[self._indices[0]]
    
    def setChid(self, chid):
        """Set chain identifier."""
        
        self.setChids(chid)
    
    def getSequence(self, **kwargs):
        """Return one-letter sequence string for amino acids in the chain.  
        When *allres* keyword argument is **True**, sequence will include all 
        residues (e.g. water molecules) in the chain and **X** will be used for 
        non-standard residue names."""
        
        if kwargs.get('allres', False):
            get = AAMAP.get
            seq = ''.join([get(res.getResname(), 'X') for res in self._list])
        elif self._seq:
            seq = self._seq
        else:
            calpha = self.calpha
            if calpha:
                seq = getSequence(calpha.getResnames())
            else:    
                seq = ''
            self._seq = seq
        return seq
    
    def getSelstr(self):
        """Return selection string that selects atoms in this chain."""

        if self._segment is None:        
            if self._selstr:
                return 'chain {0:s} and ({1:s})'.format(
                        self.getChid(), self._selstr)
            else:
                return 'chain {0:s}'.format(self.getChid())
        else:
            return 'chain {0:s} and ({1:s})'.format(
                    self.getChid(), self._segment.getSelstr())
